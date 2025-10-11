import pytest
from typing import Optional
from sqlalchemy import create_engine, String, Integer, Boolean, Text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

from SARepo.sa_repo import SARepository
from SARepo.base import NotFoundError



class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    age: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    note: Mapped[Optional[str]] = mapped_column(Text)



@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    with SessionLocal() as s:
        yield s


@pytest.fixture()
def repo(session):
    return SARepository(Item, session)


def seed(session, repo):
    """Наполняем базу различными записями для агрегатов/фильтров."""
    data = [
        Item(title="alpha",  city="Almaty",   amount=10, age=20, note="A"),
        Item(title="beta",   city="Astana",   amount=20, age=30, note="B"),
        Item(title="gamma",  city="Almaty",   amount=30, age=40, note="G"),
        Item(title="delta",  city="Shymkent", amount=40, age=50, note="D"),
        Item(title="omega",  city=None,       amount=50, age=60, note="O"),
    ]
    for obj in data:
        repo.add(obj)
    session.commit()



def test_get_or_create(session, repo):
    seed(session, repo)

    obj, created = repo.get_or_create(title="alpha", defaults={"city": "Kokshetau"})
    assert created is False
    assert obj.city == "Almaty"

    obj2, created2 = repo.get_or_create(title="sigma", defaults={"city": "Aktau", "amount": 77})
    assert created2 is True
    assert (obj2.title, obj2.city, obj2.amount) == ("sigma", "Aktau", 77)


def test_raw_query(session, repo):
    seed(session, repo)

    rows = repo.raw_query(
        "SELECT id, title, city FROM items WHERE lower(title) LIKE :p",
        {"p": "%a%"}
    )
    assert isinstance(rows, list) and all(isinstance(r, dict) for r in rows)
    titles = {r["title"] for r in rows}
    assert {"alpha", "gamma", "delta"}.issubset(titles)


def test_aggregates_avg_min_max_sum_ignore_soft_deleted_by_default(session, repo):
    seed(session, repo)

    omega = repo.find_all_by_column("title", "omega")[0]
    omega.is_deleted = True
    session.commit()

    avg_amount = repo.aggregate_avg("amount")
    min_amount = repo.aggregate_min("amount")
    max_amount = repo.aggregate_max("amount")
    sum_amount = repo.aggregate_sum("amount")

    assert avg_amount == pytest.approx((10 + 20 + 30 + 40) / 4)
    assert min_amount == 10
    assert max_amount == 40
    assert sum_amount == 10 + 20 + 30 + 40

    avg_age_almaty = repo.aggregate_avg("age", city="Almaty")
    assert avg_age_almaty == pytest.approx((20 + 40) / 2)


def test_count_with_and_without_deleted(session, repo):
    seed(session, repo)

    for t in ("alpha", "beta"):
        x = repo.find_all_by_column("title", t)[0]
        x.is_deleted = True
    session.commit()

    assert repo.count() == 3

    assert repo.count(include_deleted=True) == 5

    assert repo.count(city="Almaty") == 1 


def test_restore(session, repo):
    seed(session, repo)

    beta = repo.find_all_by_column("title", "beta")[0]
    beta.is_deleted = False
    session.commit()
    
    deleted = repo.remove(id=beta.id)
    print("DELETED ", deleted)

    ok = repo.restore(beta.id)
    assert ok is True
    session.commit()

    ok2 = repo.restore(beta.id)
    assert ok2 is False

    assert repo.count() == 5
