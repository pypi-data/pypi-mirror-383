
import pytest
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from SARepoo.sa_repo import SARepository
from SARepoo.base import PageRequest

class Base(DeclarativeBase): pass

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))

def test_crud_and_pagination():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        repo = SARepository(Item, session)
        for i in range(25):
            repo.add(Item(title=f"t{i}"))
        session.commit()

        page = repo.page(PageRequest(1, 10))
        assert page.total == 25
        assert len(page.items) == 10
        assert page.page == 1
        assert page.pages == 3
