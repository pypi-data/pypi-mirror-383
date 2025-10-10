
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

class UoW(AbstractContextManager):
    """Minimal Unit of Work for sync SQLAlchemy sessions."""
    def __init__(self, session: Session):
        self.session = session
    def __enter__(self):
        return self
    def __exit__(self, exc_type, *_):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()

class AsyncUoW:
    """Minimal Unit of Work for async SQLAlchemy sessions."""
    def __init__(self, session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, *_):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
