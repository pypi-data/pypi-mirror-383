"""Base model definitions for workspaceflow"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, TypeDecorator, String, CHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, UUID):
                return str(UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, UUID):
                value = UUID(value)
            return value


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class UUIDMixin:
    """Mixin for UUID primary key"""

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
        nullable=False
    )
