
from typing import Callable
from sqlalchemy.sql import Select

Spec = Callable[[Select], Select]

def and_specs(*specs: Spec) -> Spec:
    def _apply(q: Select) -> Select:
        for s in specs:
            q = s(q)
        return q
    return _apply

def eq(model_attr, value) -> Spec:
    def _s(q: Select) -> Select:
        return q.where(model_attr == value)
    return _s

def ilike(model_attr, pattern: str) -> Spec:
    def _s(q: Select) -> Select:
        return q.where(model_attr.ilike(pattern))
    return _s

def not_deleted(model_cls) -> Spec:
    def _s(q: Select) -> Select:
        return q.where(getattr(model_cls, "is_deleted") == False)  # noqa: E712
    return _s
