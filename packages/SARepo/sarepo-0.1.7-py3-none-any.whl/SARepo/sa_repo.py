from typing import List, Type, Generic, TypeVar, Optional, Sequence, Any, Callable
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select, func, text
from .base import PageRequest, Page, NotFoundError

T = TypeVar("T")
Spec = Callable


class SARepository(Generic[T]):
    """Synchronous repository implementation for SQLAlchemy 2.x."""

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def _resolve_column(self, column_name: str):
        try:
            return getattr(self.model, column_name)
        except AttributeError as e:
            raise ValueError(f"Model {self.model.__name__} has no column '{column_name}'") from e

    def _apply_filters(self, stmt, **filters):
        if filters:
            stmt = stmt.filter_by(**filters)
        return stmt

    def _select(self):
        return select(self.model)

    def _has_soft_delete(self) -> bool:
        return hasattr(self.model, "is_deleted")

    def _apply_alive_filter(self, stmt, include_deleted: bool):
        if self._has_soft_delete() and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        return stmt

    def getAll(
            self,
            limit: Optional[int] = None,
            *,
            include_deleted: bool = False,
            order_by=None,
            **filters
    ) -> List[T]:
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, **filters)
        stmt = self._apply_alive_filter(stmt, include_deleted)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> T:
        if id_ is not None:
            obj = self.session.get(self.model, id_)
            if not obj:
                raise NotFoundError(f"{self.model.__name__}({id_}) not found")
        else:
            stmt = select(self.model)
            stmt = self._apply_filters(stmt, **filters)
            stmt = self._apply_alive_filter(stmt, include_deleted)
            res = self.session.execute(stmt)
            obj = res.scalars().first()
            if not obj:
                raise NotFoundError(f"{self.model.__name__} not found for {filters}")
        if self._has_soft_delete() and not include_deleted and getattr(obj, "is_deleted", False):
            raise NotFoundError(f"{self.model.__name__}({getattr(obj, 'id', '?')}) deleted")
        return obj

    def try_get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> Optional[T]:
        try:
            return self.get(id_=id_, include_deleted=include_deleted, **filters)
        except NotFoundError:
            return None

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def remove(self, entity: Optional[T] = None, id: Optional[Any] = None) -> bool:
        if entity is None and id is None:
            raise ValueError("remove() requires either entity or id")

        if id is not None:
            return self._delete_by_id(id)

        insp = inspect(entity, raiseerr=False)
        if not (insp and (insp.persistent or insp.pending)):
            pk = getattr(entity, "id", None)
            if pk is None:
                raise ValueError("remove() needs a persistent entity or an entity with a primary key set")
            entity = self.session.get(self.model, pk)
            if entity is None:
                return False
        if hasattr(entity, "is_deleted"):
            setattr(entity, "is_deleted", True)
        else:
            self.session.delete(entity)

        return True

    def _delete_by_id(self, id_: Any) -> bool:
        obj = self.session.get(self.model, id_)
        if not obj:
            return False
        self.remove(obj)
        return True

    def page(self, page: PageRequest, spec: Optional[Spec] = None, order_by=None, *, include_deleted: bool = False) -> \
    Page[T]:
        base = self._select()
        if spec:
            base = spec(base)
        base = self._apply_alive_filter(base, include_deleted)
        if order_by is not None:
            base = base.order_by(order_by)

        total = self.session.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar_one()

        items = self.session.execute(
            base.offset(page.page * page.size).limit(page.size)
        ).scalars().all()
        return Page(items, total, page.page, page.size)

    def get_all_by_column(
            self,
            column_name: str,
            value: Any,
            *,
            limit: Optional[int] = None,
            order_by=None,
            include_deleted: bool = False,
            **extra_filters
    ) -> list[T]:
        col = self._resolve_column(column_name)
        stmt = select(self.model).where(col == value)
        stmt = self._apply_alive_filter(stmt, include_deleted)
        stmt = self._apply_filters(stmt, **extra_filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        res = self.session.execute(stmt)
        return res.scalars().all()

    # Alias 
    def find_all_by_column(self, *args, **kwargs):
        return self.get_all_by_column(*args, **kwargs)

    def get_or_create(
            self,
            defaults: Optional[dict] = None,
            **unique_filters
    ) -> tuple[T, bool]:
        """
        Возвращает (obj, created). unique_filters определяют уникальность.
        defaults дополняют поля при создании.
        """
        stmt = select(self.model).filter_by(**unique_filters)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        obj = self.session.execute(stmt).scalar_one_or_none()
        if obj:
            return obj, False
        payload = {**unique_filters, **(defaults or {})}
        obj = self.model(**payload)  # type: ignore[call-arg]
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj, True

    def raw_query(self, sql: str, params: Optional[dict] = None) -> list[dict]:
        """
        Безопасно выполняет сырой SQL (используй плейсхолдеры :name).
        Возвращает список dict (строки).
        """
        res = self.session.execute(text(sql), params or {})
        # mapping() -> RowMapping (dict-like)
        return [dict(row) for row in res.mappings().all()]

    def aggregate_avg(self, column_name: str, **filters) -> Optional[float]:
        col = self._resolve_column(column_name)
        stmt = select(func.avg(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        stmt = self._apply_filters(stmt, **filters)
        return self.session.execute(stmt).scalar()

    def aggregate_min(self, column_name: str, **filters):
        col = self._resolve_column(column_name)
        stmt = select(func.min(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = self._apply_filters(stmt, **filters)
        return self.session.execute(stmt).scalar()

    def aggregate_max(self, column_name: str, **filters):
        col = self._resolve_column(column_name)
        stmt = select(func.max(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = self._apply_filters(stmt, **filters)
        return self.session.execute(stmt).scalar()

    def aggregate_sum(self, column_name: str, **filters):
        col = self._resolve_column(column_name)
        stmt = select(func.sum(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = self._apply_filters(stmt, **filters)
        return self.session.execute(stmt).scalar()

    def count(self, **filters) -> int:
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted") and not filters.pop("include_deleted", False):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        if filters:
            stmt = stmt.filter_by(**filters)
        return int(self.session.execute(stmt).scalar_one())

    def restore(self, id_: Any) -> bool:
        """
        Для soft-delete: is_deleted=False. Возвращает True, если восстановили.
        """
        if not hasattr(self.model, "is_deleted"):
            raise RuntimeError(f"{self.model.__name__} has no 'is_deleted' field")
        obj = self.session.get(self.model, id_)
        if not obj:
            return False
        if getattr(obj, "is_deleted", False):
            setattr(obj, "is_deleted", False)
            self.session.flush()
            return True
        return False


class SAAsyncRepository(Generic[T]):
    """Async repository implementation for SQLAlchemy 2.x."""

    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    def _resolve_column(self, column_name: str):
        try:
            return getattr(self.model, column_name)
        except AttributeError as e:
            raise ValueError(f"Model {self.model.__name__} has no column '{column_name}'") from e

    def _apply_filters(self, stmt, **filters):
        if filters:
            stmt = stmt.filter_by(**filters)
        return stmt

    def _select(self):
        return select(self.model)

    def _has_soft_delete(self) -> bool:
        return hasattr(self.model, "is_deleted")

    def _apply_alive_filter(self, stmt, include_deleted: bool):
        if self._has_soft_delete() and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        return stmt

    async def getAll(
            self,
            limit: Optional[int] = None,
            *,
            include_deleted: bool = False,
            order_by=None,
            **filters
    ) -> List[T]:
        """
        Получить все записи с возможностью фильтрации (username='foo', age__gt=20, и т.д.)
        """
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, **filters)
        stmt = self._apply_alive_filter(stmt, include_deleted)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> T:
        """
        Получить один объект по id или по произвольным фильтрам.
        Пример:
            await repo.get(id_=1)
            await repo.get(username='ibrahim')
            await repo.get(username__ilike='%rah%')
        """
        if id_ is not None:
            obj = await self.session.get(self.model, id_)
            if not obj:
                raise NotFoundError(f"{self.model.__name__}({id_}) not found")
        else:
            stmt = select(self.model)
            stmt = self._apply_filters(stmt, **filters)
            stmt = self._apply_alive_filter(stmt, include_deleted)
            res = await self.session.execute(stmt)
            obj = res.scalars().first()
            if not obj:
                raise NotFoundError(f"{self.model.__name__} not found for {filters}")
        if self._has_soft_delete() and not include_deleted and getattr(obj, "is_deleted", False):
            raise NotFoundError(f"{self.model.__name__}({getattr(obj, 'id', '?')}) deleted")
        return obj

    async def try_get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> Optional[T]:
        """
        Как get(), но не выбрасывает исключение при отсутствии объекта.
        """
        try:
            return await self.get(id_=id_, include_deleted=include_deleted, **filters)
        except NotFoundError:
            return None

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def remove(self, entity: Optional[T] = None, id: Optional[Any] = None) -> bool:
        if entity is None and id is None:
            raise ValueError("remove() requires either entity or id")

        if id is not None:
            return await self._delete_by_id(id)

        insp = inspect(entity, raiseerr=False)
        if not (insp and (insp.persistent or insp.pending)):
            pk = getattr(entity, "id", None)
            if pk is None:
                raise ValueError("remove() needs a persistent entity or an entity with a primary key set")
            entity = await self.session.get(self.model, pk)
            if entity is None:
                return False
        if hasattr(entity, "is_deleted"):
            setattr(entity, "is_deleted", True)
        else:
            await self.session.delete(entity)

        return True

    async def _delete_by_id(self, id_: Any) -> bool:
        obj = await self.session.get(self.model, id_)
        if not obj:
            return False
        await self.remove(obj)
        return True

    async def page(self, page: PageRequest, spec: Optional[Spec] = None, order_by=None, *,
                   include_deleted: bool = False) -> Page[T]:  # type: ignore
        base = self._select()
        if spec:
            base = spec(base)
        base = self._apply_alive_filter(base, include_deleted)
        if order_by is not None:
            base = base.order_by(order_by)

        total = (await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar_one()

        res = await self.session.execute(
            base.offset(page.page * page.size).limit(page.size)
        )
        items = res.scalars().all()
        return Page(items, total, page.page, page.size)

    async def get_all_by_column(
            self,
            column_name: str,
            value: Any,
            *,
            limit: Optional[int] = None,
            order_by=None,
            include_deleted: bool = False,
            **extra_filters
    ) -> list[T]:
        col = self._resolve_column(column_name)
        stmt = select(self.model).where(col == value)
        stmt = self._apply_alive_filter(stmt, include_deleted)
        stmt = self._apply_filters(stmt, **extra_filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # Alias
    async def find_all_by_column(self, *args, **kwargs):
        return await self.get_all_by_column(*args, **kwargs)

    async def get_or_create(
            self,
            defaults: Optional[dict] = None,
            **unique_filters
    ) -> tuple[T, bool]:
        stmt = select(self.model).filter_by(**unique_filters)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        obj = (await self.session.execute(stmt)).scalar_one_or_none()
        if obj:
            return obj, False
        payload = {**unique_filters, **(defaults or {})}
        obj = self.model(**payload)  # type: ignore[call-arg]
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj, True

    async def raw_query(self, sql: str, params: Optional[dict] = None) -> list[dict]:
        res = await self.session.execute(text(sql), params or {})
        return [dict(row) for row in res.mappings().all()]

    async def aggregate_avg(self, column_name: str, **filters) -> Optional[float]:
        col = self._resolve_column(column_name)
        stmt = select(func.avg(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        stmt = self._apply_filters(stmt, **filters)
        return (await self.session.execute(stmt)).scalar()

    async def aggregate_min(self, column_name: str, **filters):
        col = self._resolve_column(column_name)
        stmt = select(func.min(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = self._apply_filters(stmt, **filters)
        return (await self.session.execute(stmt)).scalar()

    async def aggregate_max(self, column_name: str, **filters):
        col = self._resolve_column(column_name)
        stmt = select(func.max(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = self._apply_filters(stmt, **filters)
        return (await self.session.execute(stmt)).scalar()

    async def aggregate_sum(self, column_name: str, **filters):
        col = self._resolve_column(column_name)
        stmt = select(func.sum(col))
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = self._apply_filters(stmt, **filters)
        return (await self.session.execute(stmt)).scalar()

    async def count(self, **filters) -> int:
        include_deleted = bool(filters.pop("include_deleted", False))
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        if filters:
            stmt = stmt.filter_by(**filters)
        return int((await self.session.execute(stmt)).scalar_one())

    async def restore(self, id_: Any) -> bool:
        if not hasattr(self.model, "is_deleted"):
            raise RuntimeError(f"{self.model.__name__} has no 'is_deleted' field")
        obj = await self.session.get(self.model, id_)
        if not obj:
            return False
        if getattr(obj, "is_deleted", False):
            setattr(obj, "is_deleted", False)
            await self.session.flush()
            return True
        return False