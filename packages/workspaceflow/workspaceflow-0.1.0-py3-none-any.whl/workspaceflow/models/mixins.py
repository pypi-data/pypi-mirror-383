"""Mixins for workspace-scoped data isolation"""

from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from workspaceflow.models.base import GUID


class WorkspaceScopedMixin:
    """
    Mixin for workspace-scoped models to ensure data isolation by workspace_id.

    Any model that includes this mixin will automatically have a workspace_id
    foreign key and helper methods for workspace-scoped queries.

    Example:
        class Contract(Base, WorkspaceScopedMixin):
            __tablename__ = "contracts"

            id: Mapped[UUID] = mapped_column(primary_key=True)
            title: Mapped[str] = mapped_column(String(255))
            # workspace_id is automatically added by the mixin

        # Query contracts for a specific workspace
        contracts = Contract.query_for_workspace(db, workspace_id)
    """

    workspace_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    @classmethod
    def query_for_workspace(cls, db: Session, workspace_id: UUID):
        """
        Query helper to filter records by workspace_id.

        Args:
            db: SQLAlchemy session
            workspace_id: UUID of the workspace to filter by

        Returns:
            Query object filtered by workspace_id
        """
        return db.query(cls).filter(cls.workspace_id == workspace_id)
