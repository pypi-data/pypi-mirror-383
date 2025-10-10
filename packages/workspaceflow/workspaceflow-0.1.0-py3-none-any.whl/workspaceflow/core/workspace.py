"""Workspace service with authflow integration"""

from uuid import UUID
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from workspaceflow.models.workspace import Workspace
from workspaceflow.models.workspace_team import WorkspaceTeam
from workspaceflow.exceptions import (
    WorkspaceNotFoundError,
    WorkspaceSlugConflictError,
    TeamAlreadyAssignedError,
    TeamNotAssignedError,
    WorkspacePermissionDeniedError
)
from workspaceflow.utils.slug import generate_slug, ensure_unique_slug
from workspaceflow.config import WorkspaceConfig


class WorkspaceService:
    """
    Service for workspace/project management with authflow integration.

    This service handles CRUD operations for workspaces and integrates
    with authflow for authentication, authorization, and team management.

    Example:
        from authflow import AuthFlow

        authflow = AuthFlow(...)
        service = WorkspaceService(db, authflow, config)

        # Create a workspace
        workspace = service.create_workspace(
            user_id=user.id,
            org_id=org.id,
            name="Project Alpha"
        )
    """

    def __init__(
        self,
        db: Session,
        authflow: Any,  # authflow.AuthFlow instance
        config: WorkspaceConfig | None = None
    ):
        self.db = db
        self.authflow = authflow
        self.config = config or WorkspaceConfig()

    def create_workspace(
        self,
        user_id: UUID,
        org_id: UUID,
        name: str,
        description: str | None = None,
        settings: dict | None = None
    ) -> Workspace:
        """
        Create a new workspace/project.

        Args:
            user_id: ID of the user creating the workspace
            org_id: ID of the organization the workspace belongs to
            name: Name of the workspace
            description: Optional description
            settings: Optional workspace settings

        Returns:
            The created Workspace

        Raises:
            WorkspacePermissionDeniedError: If user lacks permission
            WorkspaceSlugConflictError: If slug already exists
        """
        # Check permission via authflow
        if not self.authflow.has_permission(user_id, f"org:{org_id}:workspaces:create"):
            raise WorkspacePermissionDeniedError(
                permission=f"org:{org_id}:workspaces:create"
            )

        # Generate unique slug
        base_slug = generate_slug(name, max_length=self.config.slug_max_length)
        existing_slugs = {
            ws.slug for ws in self.db.query(Workspace.slug).all()
        }
        slug = ensure_unique_slug(base_slug, existing_slugs)

        # Create workspace
        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            organization_id=org_id,
            settings=settings or {}
        )

        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)

        return workspace

    def get_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID | None = None,
        load_teams: bool = True
    ) -> Workspace:
        """
        Get a workspace by ID.

        Args:
            workspace_id: ID of the workspace
            user_id: Optional user ID (for permission checks, currently unused)
            load_teams: Whether to eager load team assignments

        Returns:
            The Workspace

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
        """
        query = self.db.query(Workspace).filter(Workspace.id == workspace_id)

        if load_teams:
            query = query.options(selectinload(Workspace.team_assignments))

        workspace = query.first()

        if not workspace:
            raise WorkspaceNotFoundError(str(workspace_id))

        return workspace

    def get_workspace_by_slug(self, slug: str) -> Workspace:
        """Get a workspace by slug"""
        workspace = self.db.query(Workspace).filter(Workspace.slug == slug).first()

        if not workspace:
            raise WorkspaceNotFoundError(f"slug:{slug}")

        return workspace

    def list_workspaces(
        self,
        org_id: UUID,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> list[Workspace]:
        """
        List workspaces in an organization.

        Returns workspaces the user can access via team membership, or all
        workspaces in the org if user has no team restrictions.

        Args:
            org_id: Organization ID
            user_id: User ID for filtering (required)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of Workspaces
        """
        query = self.db.query(Workspace).filter(
            Workspace.organization_id == org_id
        )

        # Get user's teams to filter workspaces
        user_teams = self.authflow.get_user_teams(user_id, org_id)

        if user_teams:
            # Filter by user's team memberships
            team_ids = [t.id if hasattr(t, 'id') else t.get('id') for t in user_teams]

            query = query.join(WorkspaceTeam).filter(
                WorkspaceTeam.team_id.in_(team_ids)
            ).distinct()

        return query.limit(limit).offset(offset).all()

    def update_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        settings: dict | None = None
    ) -> Workspace:
        """
        Update a workspace.

        Args:
            workspace_id: ID of the workspace to update
            user_id: ID of the user making the update
            name: New name (optional)
            description: New description (optional)
            settings: New settings (optional)

        Returns:
            The updated Workspace

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspacePermissionDeniedError: If user lacks permission
        """
        workspace = self.get_workspace(workspace_id)

        # Check permission
        if not self.authflow.has_permission(
            user_id, f"workspace:{workspace_id}:settings:write"
        ):
            raise WorkspacePermissionDeniedError(
                permission=f"workspace:{workspace_id}:settings:write"
            )

        # Update fields
        if name is not None:
            workspace.name = name
            # Regenerate slug if name changed
            base_slug = generate_slug(name, max_length=self.config.slug_max_length)
            existing_slugs = {
                ws.slug for ws in self.db.query(Workspace.slug).filter(
                    Workspace.id != workspace_id
                ).all()
            }
            workspace.slug = ensure_unique_slug(base_slug, existing_slugs)

        if description is not None:
            workspace.description = description

        if settings is not None:
            workspace.settings = settings

        self.db.commit()
        self.db.refresh(workspace)

        return workspace

    def delete_workspace(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Delete a workspace.

        Args:
            workspace_id: ID of the workspace to delete
            user_id: ID of the user performing the deletion

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspacePermissionDeniedError: If user lacks permission
        """
        workspace = self.get_workspace(workspace_id)

        # Check permission
        if not self.authflow.has_permission(
            user_id, f"workspace:{workspace_id}:delete"
        ):
            raise WorkspacePermissionDeniedError(
                permission=f"workspace:{workspace_id}:delete"
            )

        self.db.delete(workspace)
        self.db.commit()

    def assign_team(
        self,
        workspace_id: UUID,
        team_id: UUID,
        user_id: UUID,
        role: str | None = None
    ) -> WorkspaceTeam:
        """
        Assign a team to a workspace.

        Args:
            workspace_id: ID of the workspace
            team_id: ID of the team to assign
            user_id: ID of the user making the assignment
            role: Optional project-specific role for the team

        Returns:
            The WorkspaceTeam assignment

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            TeamAlreadyAssignedError: If team is already assigned
            WorkspacePermissionDeniedError: If user lacks permission
        """
        workspace = self.get_workspace(workspace_id)

        # Check permission
        if not self.authflow.has_permission(
            user_id, f"workspace:{workspace_id}:teams:write"
        ):
            raise WorkspacePermissionDeniedError(
                permission=f"workspace:{workspace_id}:teams:write"
            )

        # Verify team exists via authflow
        team = self.authflow.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")

        # Verify team belongs to same organization
        # Convert both to strings for comparison (handle UUID/str mismatch)
        team_org_id = str(team.organization_id)
        workspace_org_id = str(workspace.organization_id)
        if team_org_id != workspace_org_id:
            raise ValueError("Team must belong to the same organization as workspace")

        # Check if already assigned
        if workspace.is_team_assigned(team_id):
            raise TeamAlreadyAssignedError(str(team_id), str(workspace_id))

        # Create assignment
        assignment = WorkspaceTeam(
            workspace_id=workspace_id,
            team_id=team_id,
            role=role
        )

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    def remove_team(
        self,
        workspace_id: UUID,
        team_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Remove a team assignment from a workspace.

        Args:
            workspace_id: ID of the workspace
            team_id: ID of the team to remove
            user_id: ID of the user performing the removal

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            TeamNotAssignedError: If team is not assigned
            WorkspacePermissionDeniedError: If user lacks permission
        """
        workspace = self.get_workspace(workspace_id)

        # Check permission
        if not self.authflow.has_permission(
            user_id, f"workspace:{workspace_id}:teams:write"
        ):
            raise WorkspacePermissionDeniedError(
                permission=f"workspace:{workspace_id}:teams:write"
            )

        # Find assignment
        assignment = self.db.query(WorkspaceTeam).filter(
            WorkspaceTeam.workspace_id == workspace_id,
            WorkspaceTeam.team_id == team_id
        ).first()

        if not assignment:
            raise TeamNotAssignedError(str(team_id), str(workspace_id))

        self.db.delete(assignment)
        self.db.commit()

    def get_workspace_members(self, workspace_id: UUID, user_id: UUID | None = None) -> list[Any]:
        """
        Get all users with access to a workspace (via team membership).

        Args:
            workspace_id: ID of the workspace
            user_id: Optional user ID (for permission checks)

        Returns:
            List of users (from authflow)

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
        """
        workspace = self.get_workspace(workspace_id, load_teams=True)

        # Get all assigned teams
        team_ids = [assignment.team_id for assignment in workspace.team_assignments]

        # Get members from each team via authflow
        all_members = []
        seen_user_ids = set()

        for team_id in team_ids:
            members = self.authflow.get_team_members(team_id)
            for member in members:
                # Handle both dict and object members
                member_id = member.get('id') if isinstance(member, dict) else member.id
                if member_id not in seen_user_ids:
                    all_members.append(member)
                    seen_user_ids.add(member_id)

        return all_members

    def check_user_access(self, workspace_id: UUID, user_id: UUID) -> bool:
        """
        Check if a user has access to a workspace via team membership.

        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user to check

        Returns:
            True if user has access, False otherwise

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
        """
        workspace = self.get_workspace(workspace_id, load_teams=True)

        # Get all assigned team IDs
        workspace_team_ids = {assignment.team_id for assignment in workspace.team_assignments}

        # Get user's teams
        user_teams = self.authflow.get_user_teams(user_id, workspace.organization_id)
        user_team_ids = {t.id if hasattr(t, 'id') else t.get('id') for t in user_teams}

        # Check if any of user's teams are assigned to the workspace
        return bool(workspace_team_ids & user_team_ids)
