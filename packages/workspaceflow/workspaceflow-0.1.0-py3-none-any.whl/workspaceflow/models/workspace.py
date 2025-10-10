"""Workspace model - represents a project within an organization"""

from uuid import UUID

from sqlalchemy import ForeignKey, JSON, String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from workspaceflow.models.base import Base, TimestampMixin, UUIDMixin, GUID
from workspaceflow.utils.slug import generate_slug, ensure_unique_slug


class Workspace(Base, UUIDMixin, TimestampMixin):
    """
    Workspace model representing a project within an organization.

    A workspace is a project that belongs to an organization (from authflow).
    Teams (from authflow) can be assigned to workspaces to grant access.
    All project data should use WorkspaceScopedMixin to ensure isolation.

    Relationships:
        - Belongs to an Organization (authflow)
        - Has many WorkspaceTeam assignments
        - All workspace-scoped data references this via workspace_id

    Example:
        # Create a workspace for an organization
        workspace = Workspace(
            name="Project Alpha",
            slug="project-alpha",
            organization_id=org.id,
            settings={"theme": "dark"}
        )
    """

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(String)

    # Link to authflow Organization (stored in Keycloak, not in database)
    # No foreign key constraint since organizations are managed externally
    organization_id: Mapped[UUID] = mapped_column(
        GUID,
        nullable=False,
        index=True
    )

    # Project-specific settings (JSON for flexibility)
    settings: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        server_default="{}",
        nullable=False
    )

    # Relationships
    team_assignments: Mapped[list["WorkspaceTeam"]] = relationship(
        "WorkspaceTeam",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    def is_team_assigned(self, team_id: UUID) -> bool:
        """Check if a team is assigned to this workspace"""
        return any(assignment.team_id == team_id for assignment in self.team_assignments)

    def get_team_role(self, team_id: UUID) -> str | None:
        """Get the role of a team in this workspace"""
        assignment = next(
            (a for a in self.team_assignments if a.team_id == team_id),
            None
        )
        return assignment.role if assignment else None


# Event listener to auto-generate slug before insert
@event.listens_for(Workspace, 'before_insert')
def generate_workspace_slug(mapper, connection, target):
    """Auto-generate slug from workspace name if not provided"""
    if not target.slug and target.name:
        base_slug = generate_slug(target.name)

        # Get existing slugs to ensure uniqueness
        existing_slugs = set()
        result = connection.execute(
            target.__table__.select().with_only_columns(target.__table__.c.slug)
        )
        for row in result:
            existing_slugs.add(row[0])

        # Ensure uniqueness
        target.slug = ensure_unique_slug(base_slug, existing_slugs)
