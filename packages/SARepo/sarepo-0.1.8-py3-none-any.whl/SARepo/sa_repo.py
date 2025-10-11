from typing import List, Type, Generic, TypeVar, Optional, Sequence, Any, Callable, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select, func, text, insert, update, and_
from .base import PageRequest, Page, NotFoundError

T = TypeVar("T")
Spec = Callable


class SARepository(Generic[T]):
    """Sync repository implementation for SQLAlchemy 2.x (ORM Session)."""

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    # ---- helpers

    def _resolve_column(self, column_name: str):
        try:
            return getattr(self.model, column_name)
        except AttributeError as e:
            raise ValueError(f"Model {self.model.__name__} has no column '{column_name}'") from e

    def _apply_filters(self, stmt, **filters):
        if filters:
            stmt = stmt.filter_by(**filters)
        return stmt

    def _to_dto(self, obj: Any) -> Any:
        if hasattr(obj, "to_read_model"):
            return obj.to_read_model()
        return obj

    def _select(self):
        return select(self.model)

    def _has_soft_delete(self) -> bool:
        return hasattr(self.model, "is_deleted")

    def _apply_alive_filter(self, stmt, include_deleted: bool):
        if self._has_soft_delete() and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        return stmt

    # ---- CRUD/queries

    def getAll(
        self,
        limit: Optional[int] = None,
        *,
        include_deleted: bool = False,
        order_by=None,
        **filters,
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
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> Optional[T]:
        """
        Получить один объект по id или по произвольным фильтрам.
            repo.get(id_=1)
            repo.get(username='ibrahim')
            repo.get(username__ilike='%rah%')   # если у тебя реализована интерпретация таких фильтров выше по стеку
        """
        if id_ is not None:
            obj = self.session.get(self.model, id_)
            if not obj:
                return None
        else:
            stmt = select(self.model)
            stmt = self._apply_filters(stmt, **filters)
            stmt = self._apply_alive_filter(stmt, include_deleted)
            res = self.session.execute(stmt)
            obj = res.scalars().first()
            if not obj:
                return None

        if self._has_soft_delete() and not include_deleted and getattr(obj, "is_deleted", False):
            raise NotFoundError(f"{self.model.__name__}({getattr(obj, 'id', '?')}) deleted")
        return obj

    def try_get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> Optional[T]:
        """Как get(), но не выбрасывает исключение при soft-deleted."""
        try:
            return self.get(id_=id_, include_deleted=include_deleted, **filters)
        except NotFoundError:
            return None

    def add(self, data: dict) -> T:
        """
        Вставка через Core insert(...).returning(model.id) — как в async-версии.
        Возвращает dict с добавленным id (повторяю твою семантику).
        """
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = self.session.execute(stmt)
        new_id = res.scalar_one()
        self.session.commit()
        data["id"] = new_id
        return data  # так же, как у тебя: возвращаем dict, а не ORM-объект

    def update(
        self,
        data: dict,
        *,
        include_deleted: bool = False,
        expect_one: bool = False,
        **filters,
    ) -> Optional[T]:
        """
        Обновляет запись(и) по произвольным фильтрам.
        Возвращает DTO одной обновлённой строки (если ровно одна) или None.
        """
        if not data:
            raise ValueError("`data` не может быть пустым.")
        if not filters:
            raise ValueError("Нужен хотя бы один фильтр (например, id=1 или username='foo').")

        values = {self._resolve_column(k).key: v for k, v in data.items()}
        conditions = [self._resolve_column(k) == v for k, v in filters.items()]
        if self._has_soft_delete() and not include_deleted:
            conditions.append(self.model.is_deleted == False)  # noqa: E712

        stmt = (
            update(self.model)
            .where(and_(*conditions))
            .values(**values)
            .returning(self.model)
        )

        res = self.session.execute(stmt)
        updated_obj = res.scalar_one_or_none()

        if expect_one:
            rowcount = res.rowcount
            if rowcount != 1:
                self.session.rollback()
                raise ValueError(f"Ожидалась ровно 1 строка, затронуто: {rowcount}")

        if updated_obj is not None:
            self.session.commit()
            return self._to_dto(updated_obj)

        self.session.rollback()
        return None

    def remove(self, entity: Optional[T] = None, id: Optional[Any] = None) -> bool:
        """
        Поведение идентично твоему async-коду: soft-delete, иначе физическое удаление.
        Коммиты намеренно не делаю, чтобы не менять твою транзакционную модель.
        """
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
            self.session.flush()
        else:
            self.session.delete(entity)

        return True

    def _delete_by_id(self, id_: Any) -> bool:
        obj = self.session.get(self.model, id_)
        if not obj:
            return False
        return self.remove(obj)

    def page(
        self,
        page: PageRequest,
        spec: Optional[Spec] = None,
        order_by=None,
        *,
        include_deleted: bool = False,
    ) -> Page[T]:  # type: ignore
        """
        Точно повторяю логику подсчёта total через подзапрос.
        Ожидается, что Page(items, total, page.page, page.size) уже есть в твоём коде.
        """
        base = self._select()
        if spec:
            base = spec(base)  # type: ignore
        base = self._apply_alive_filter(base, include_deleted)
        if order_by is not None:
            base = base.order_by(order_by)

        total = self.session.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar_one()

        res = self.session.execute(
            base.offset(page.page * page.size).limit(page.size)
        )
        items = res.scalars().all()
        return Page(items, total, page.page, page.size)  # type: ignore

    def get_all_by_column(
        self,
        column_name: str,
        value: Any,
        *,
        limit: Optional[int] = None,
        order_by=None,
        include_deleted: bool = False,
        **extra_filters,
    ) -> List[T]:
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

    # Alias — как у тебя
    def find_all_by_column(self, *args, **kwargs):
        return self.get_all_by_column(*args, **kwargs)

    def get_or_create(
        self,
        defaults: Optional[dict] = None,
        **unique_filters,
    ) -> Tuple[T, bool]:
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
        res = self.session.execute(text(sql), params or {})
        # В SQLA 2.x для маппингов:
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
        include_deleted = bool(filters.pop("include_deleted", False))
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        if filters:
            stmt = stmt.filter_by(**filters)
        return int(self.session.execute(stmt).scalar_one())

    def restore(self, id_: Any) -> bool:
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

    def _to_dto(self, obj: Any) -> Any:
        if hasattr(obj, "to_read_model"):
            return obj.to_read_model()
        return obj

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

    async def get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> Optional[T]:
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
                return None
        else:
            stmt = select(self.model)
            stmt = self._apply_filters(stmt, **filters)
            stmt = self._apply_alive_filter(stmt, include_deleted)
            res = await self.session.execute(stmt)
            obj = res.scalars().first()
            if not obj:
                return None
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

    async def add(self, data: dict) -> T:
        stmt = (
            insert(self.model)
            .values(**data)
            .returning(self.model.id)
        )
        res = await self.session.execute(stmt)
        new_id = res.scalar_one()
        await self.session.commit()
        data["id"] = new_id
        return data

    async def update(
            self,
            data: dict,
            *,
            include_deleted: bool = False,
            expect_one: bool = False,
            **filters,
    ) -> Optional[T]:
        """
        Обновляет запись(и) по произвольным фильтрам.
        - data: словарь обновляемых полей -> значений
        - include_deleted: если модель имеет is_deleted, включать ли удалённые
        - expect_one: если True — бросит ValueError, если затронуто != 1 строк
        - **filters: произвольные фильтры вида field=value
        Возвращает DTO одной обновлённой строки (если ровно одна) или None.
        """
        if not data:
            raise ValueError("`data` не может быть пустым.")
        if not filters:
            raise ValueError("Нужен хотя бы один фильтр (например, id=1 или username='foo').")

        values = {self._resolve_column(k).key: v for k, v in data.items()}

        conditions = [self._resolve_column(k) == v for k, v in filters.items()]

        if self._has_soft_delete() and not include_deleted:
            conditions.append(self.model.is_deleted == False)

        stmt = (
            update(self.model)
            .where(and_(*conditions))
            .values(**values)
            .returning(self.model)
        )

        res = await self.session.execute(stmt)
        updated_obj = res.scalar_one_or_none()

        if expect_one:
            rowcount = res.rowcount
            if rowcount != 1:
                await self.session.rollback()
                raise ValueError(f"Ожидалась ровно 1 строка, затронуто: {rowcount}")

        if updated_obj is not None:
            await self.session.commit()
            return self._to_dto(updated_obj)

        await self.session.rollback()
        return None

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