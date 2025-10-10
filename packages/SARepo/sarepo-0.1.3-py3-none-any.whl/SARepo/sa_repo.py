
from typing import List, Type, Generic, TypeVar, Optional, Sequence, Any, Callable
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select, func
from .base import PageRequest, Page, NotFoundError

T = TypeVar("T")
Spec = Callable  # aliased to match specs.Spec

class SARepository(Generic[T]):
    """Synchronous repository implementation for SQLAlchemy 2.x."""
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def _select(self):
        return select(self.model)

    def getAll(self, limit: Optional[int] = None) -> List[T]:
        stmt = select(self.model)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = self.session.execute(stmt)
        return result.scalars().all()
    
    def get(self, id_: Any) -> T:
        obj = self.session.get(self.model, id_)
        if not obj:
            raise NotFoundError(f"{self.model.__name__}({id_}) not found")
        return obj

    def try_get(self, id_: Any) -> Optional[T]:
        return self.session.get(self.model, id_)

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def remove(self, entity: T) -> None:
        insp = inspect(entity, raiseerr=False)
        if not (insp and (insp.persistent or insp.pending)):
            pk = getattr(entity, "id", None)
            if pk is None:
                raise ValueError("remove() needs a persistent entity or an entity with a primary key set")
            entity = self.session.get(self.model, pk)
            if entity is None:
                return
        if hasattr(entity, "is_deleted"):
            setattr(entity, "is_deleted", True)
        else:
            self.session.delete(entity)

    def delete_by_id(self, id_: Any) -> bool:
        obj = self.session.get(self.model, id_)
        if not obj:
            return False
        self.remove(obj)
        return True

    def page(self, page: PageRequest, spec: Optional[Spec] = None, order_by=None) -> Page[T]:
        stmt = self._select()
        if spec:
            stmt = spec(stmt)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        total = self.session.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar_one()
        items = self.session.execute(
            stmt.offset(page.page * page.size).limit(page.size)
        ).scalars().all()
        return Page(items, total, page.page, page.size)

class SAAsyncRepository(Generic[T]):
    """Async repository implementation for SQLAlchemy 2.x."""
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session
        
    async def getAll(self, limit: Optional[int] = None) -> List[T]:
        stmt = select(self.model)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _select(self):
        return select(self.model)

    async def get(self, id_: Any) -> T:
        obj = await self.session.get(self.model, id_)
        if not obj:
            raise NotFoundError(f"{self.model.__name__}({id_}) not found")
        return obj

    async def try_get(self, id_: Any) -> Optional[T]:
        return await self.session.get(self.model, id_)

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def remove(self, entity: T) -> None:
        insp = inspect(entity, raiseerr=False)
        if not (insp and (insp.persistent or insp.pending)):
            pk = getattr(entity, "id", None)
            if pk is None:
                raise ValueError("remove() needs a persistent entity or an entity with a primary key set")
            entity = await self.session.get(self.model, pk)
            if entity is None:
                return
        if hasattr(entity, "is_deleted"):
            setattr(entity, "is_deleted", True)
        else:
            await self.session.delete(entity)

    async def delete_by_id(self, id_: Any) -> bool:
        obj = await self.session.get(self.model, id_)
        if not obj:
            return False
        await self.remove(obj)
        return True

    async def page(self, page: PageRequest, spec: Optional[Spec] = None, order_by=None) -> Page[T]:
        stmt = self._select()
        if spec:
            stmt = spec(stmt)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        total = (await self.session.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar_one()
        res = await self.session.execute(
            stmt.offset(page.page * page.size).limit(page.size)
        )
        items = res.scalars().all()
        return Page(items, total, page.page, page.size)
