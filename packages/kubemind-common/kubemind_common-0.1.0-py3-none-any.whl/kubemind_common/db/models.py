"""SQLAlchemy base models and reusable mixins."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models.

    Usage:
        from kubemind_common.db.models import Base

        class User(Base):
            __tablename__ = "users"
            ...
    """

    pass


class TimestampMixin:
    """Mixin for automatic created_at and updated_at timestamps.

    Adds two columns:
        - created_at: Timestamp of record creation (server default)
        - updated_at: Timestamp of last update (auto-updated on modification)

    Usage:
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )


class UUIDMixin:
    """Mixin for UUID primary key.

    Adds a UUID primary key column named 'id'.

    Usage:
        class User(Base, UUIDMixin):
            __tablename__ = "users"
            name: Mapped[str]
    """

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        comment="Primary key UUID"
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality.

    Adds columns:
        - is_deleted: Boolean flag for soft deletion
        - deleted_at: Timestamp of deletion (nullable)

    Usage:
        class User(Base, SoftDeleteMixin):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

        # In queries, filter out deleted records:
        session.query(User).filter(User.is_deleted == False).all()
    """

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete flag"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when record was soft deleted"
    )

    def soft_delete(self) -> None:
        """Mark this record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """Mixin for audit trail (created_by, updated_by).

    Adds columns to track which user created/updated the record.

    Usage:
        class Playbook(Base, AuditMixin):
            __tablename__ = "playbooks"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

        # When creating:
        playbook = Playbook(name="test", created_by=current_user.id)
        # When updating:
        playbook.updated_by = current_user.id
    """

    created_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="User ID who created this record"
    )
    updated_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="User ID who last updated this record"
    )


class FullAuditMixin(TimestampMixin, AuditMixin):
    """Combined mixin for timestamps and user audit trail.

    Includes both timestamp tracking (created_at, updated_at)
    and user tracking (created_by, updated_by).

    Usage:
        class Cluster(Base, UUIDMixin, FullAuditMixin):
            __tablename__ = "clusters"
            name: Mapped[str]
    """

    pass


class ActiveRecordMixin:
    """Mixin for is_active flag.

    Adds a boolean column to track if record is active/enabled.

    Usage:
        class APIKey(Base, ActiveRecordMixin):
            __tablename__ = "api_keys"
            id: Mapped[int] = mapped_column(primary_key=True)
            key_hash: Mapped[str]
    """

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether record is active"
    )


# Common combined base classes for convenience

class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Standard base model with UUID primary key and timestamps.

    Includes:
        - id (UUID primary key)
        - created_at
        - updated_at

    Usage:
        class Event(BaseModel):
            __tablename__ = "events"
            source: Mapped[str]
            type: Mapped[str]
    """

    __abstract__ = True


class AuditedModel(Base, UUIDMixin, FullAuditMixin):
    """Audited base model with UUID, timestamps, and user tracking.

    Includes:
        - id (UUID primary key)
        - created_at, updated_at
        - created_by, updated_by

    Usage:
        class Playbook(AuditedModel):
            __tablename__ = "playbooks"
            name: Mapped[str]
            spec: Mapped[dict]
    """

    __abstract__ = True


class SoftDeleteModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Base model with soft delete support.

    Includes:
        - id (UUID primary key)
        - created_at, updated_at
        - is_deleted, deleted_at

    Usage:
        class User(SoftDeleteModel):
            __tablename__ = "users"
            email: Mapped[str]
            password_hash: Mapped[str]
    """

    __abstract__ = True


class FullAuditedModel(Base, UUIDMixin, FullAuditMixin, SoftDeleteMixin, ActiveRecordMixin):
    """Fully-featured base model with all audit capabilities.

    Includes:
        - id (UUID primary key)
        - created_at, updated_at
        - created_by, updated_by
        - is_deleted, deleted_at
        - is_active

    Usage:
        class Investigation(FullAuditedModel):
            __tablename__ = "investigations"
            title: Mapped[str]
            status: Mapped[str]
    """

    __abstract__ = True


def to_dict(model: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """Convert SQLAlchemy model instance to dictionary.

    Args:
        model: SQLAlchemy model instance
        exclude: Set of column names to exclude

    Returns:
        Dictionary representation of model

    Usage:
        user = session.get(User, user_id)
        user_dict = to_dict(user, exclude={'password_hash'})
    """
    exclude = exclude or set()
    result = {}

    for column in model.__table__.columns:
        if column.name not in exclude:
            value = getattr(model, column.name)
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value

    return result
