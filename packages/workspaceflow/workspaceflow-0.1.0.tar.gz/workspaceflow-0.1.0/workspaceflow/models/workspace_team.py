"""WorkspaceTeam model - assignment of teams to projects"""

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workspaceflow.models.base import Base, TimestampMixin, UUIDMixin, GUID


class WorkspaceTeam(Base, UUIDMixin, TimestampMixin):
    """
    WorkspaceTeam represents the assignment of an authflow Team to a Workspace (project).

    When a team is assigned to a workspace, all members of that team
    gain access to the workspace and its data.

    Attributes:
        workspace_id: The workspace/project being accessed
        team_id: The authflow team being granted access
        role: Optional project-specific role for the team (e.g., "admin", "contributor", "viewer")
        created_at: When the assignment was created (from TimestampMixin)
        updated_at: When the assignment was last updated (from TimestampMixin)

    Example:
        # Assign Team A to Project Alpha with admin role
        assignment = WorkspaceTeam(
            workspace_id=workspace.id,
            team_id=team_a.id,
            role="admin"
        )
    """

    __tablename__ = "workspace_teams"
    __table_args__ = (
        UniqueConstraint('workspace_id', 'team_id', name='uq_workspace_team'),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Links to authflow Team (stored in Keycloak, not in database)
    # No foreign key constraint since teams are managed externally
    team_id: Mapped[UUID] = mapped_column(
        GUID,
        nullable=False,
        index=True
    )

    # Optional: team-specific role within this workspace
    # If None, team uses their default permissions
    role: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="team_assignments"
    )

    def __repr__(self) -> str:
        return (
            f"<WorkspaceTeam(workspace_id={self.workspace_id}, "
            f"team_id={self.team_id}, role='{self.role}')>"
        )
