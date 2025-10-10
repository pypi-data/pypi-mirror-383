import pytest
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from SARepo.sa_repo import SARepository
from SARepo.base import PageRequest, NotFoundError

class Base(DeclarativeBase): pass

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

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
        # проверим, что конкретные объекты есть
        got = {it.title for it in page.items}
        assert got.issubset({f"t{i}" for i in range(25)})

def test_get_all():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        repo = SARepository(Item, session)
        for i in range(10):
            repo.add(Item(title=f"get-all-{i}"))
        session.commit()

        items = repo.getAll()
        assert isinstance(items, list)
        assert len(items) == 10
        titles = {i.title for i in items}
        assert titles == {f"get-all-{i}" for i in range(10)}
        
        items2 = repo.getAll(5)
        assert isinstance(items2, list)
        assert len(items2) == 5
        titles = {i.title for i in items2}
        assert titles == {f"get-all-{i}" for i in range(5)}

def test_get_and_try_get():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        repo = SARepository(Item, session)
        obj = repo.add(Item(title="one"))
        session.commit()

        same = repo.get(obj.id)
        assert same.id == obj.id and same.title == "one"

        assert repo.try_get(9999) is None

        with pytest.raises(NotFoundError):
            repo.get(9999)
