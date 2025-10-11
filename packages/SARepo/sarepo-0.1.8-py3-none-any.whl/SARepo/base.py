
from typing import Generic, TypeVar, Sequence
T = TypeVar("T")

class NotFoundError(Exception):
    """Raised when entity not found."""
    pass

class ConcurrencyError(Exception):
    """Raised when optimistic lock/version conflicts occur."""
    pass

class PageRequest:
    def __init__(self, page: int = 0, size: int = 10):
        if page < 0:
            raise ValueError("page must be >= 0")
        if not (1 <= size <= 10000):
            raise ValueError("size must be in [1, 10000]")
        self.page = page
        self.size = size

class Page(Generic[T]):
    def __init__(self, items: Sequence[T], total: int, page: int, size: int):
        self.items = list(items)
        self.total = int(total)
        self.page = int(page)
        self.size = int(size)

    @property
    def pages(self) -> int:
        return (self.total + self.size - 1) // self.size
