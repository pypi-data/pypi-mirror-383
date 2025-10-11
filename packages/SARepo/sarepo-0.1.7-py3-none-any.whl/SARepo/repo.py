from typing import Generic, List, TypeVar, Type, Optional, Any, Protocol

from SARepo.sa_repo import Spec
from .base import Page, PageRequest

T = TypeVar("T")


class CrudRepository(Protocol, Generic[T]):
    model: Type[T]

    def getAll(self,
               limit: Optional[int] = None,
               *,
               include_deleted: bool = False,
               order_by=None,
               **filters) -> List[T]: ...

    def get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> T: ...

    def try_get(self, id_: Any = None, *, include_deleted: bool = False, **filters) -> Optional[T]: ...

    def add(self, entity: T) -> T: ...

    def update(self, entity: T) -> T: ...

    def remove(self, entity: Optional[T] = None, id: Optional[Any] = None) -> bool: ...

    def delete_by_id(self, id_: Any) -> bool: ...

    def page(self, page: PageRequest, spec: Optional[Spec] = None, order_by=None, *, include_deleted: bool = False) -> \
    Page[T]: ...

    def get_all_by_column(
            self,
            column_name: str,
            value: Any,
            *,
            limit: Optional[int] = None,
            order_by=None,
            include_deleted: bool = False,
            **extra_filters
    ) -> list[T]: ...

    def find_all_by_column(
            self,
            column_name: str,
            value: Any,
            *,
            limit: Optional[int] = None,
            order_by=None,
            include_deleted: bool = False,
            **extra_filters
    ) -> list[T]: ...

    def get_or_create(
            self,
            defaults: Optional[dict] = None,
            **unique_filters
    ) -> tuple[T, bool]: ...

    def raw_query(self, sql: str, params: Optional[dict] = None) -> list[dict]: ...

    def aggregate_avg(self, column_name: str, **filters) -> Optional[float]: ...

    def aggregate_min(self, column_name: str, **filters): ...

    def aggregate_max(self, column_name: str, **filters): ...

    def aggregate_sum(self, column_name: str, **filters): ...

    def count(self, **filters) -> int: ...

    def restore(self, id_: Any) -> bool: ...
