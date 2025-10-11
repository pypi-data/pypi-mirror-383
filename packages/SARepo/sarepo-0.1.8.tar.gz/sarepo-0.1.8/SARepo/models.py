
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, DateTime, Boolean

class Base(DeclarativeBase):
    """Base for user models if you don't want to declare your own."""
    pass

class TimeStamped:
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SoftDelete:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
