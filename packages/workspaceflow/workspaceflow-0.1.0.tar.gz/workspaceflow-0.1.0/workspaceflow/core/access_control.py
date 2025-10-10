"""Access control helpers for workspace team-based permissions"""

from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from workspaceflow.models.workspace import Workspace
from workspaceflow.models.workspace_team import WorkspaceTeam


def check_workspace_access(
    db: Session,
    workspace_id: UUID,
    user_id: UUID,
    authflow: Any
) -> bool:
    """
    Check if a user has access to a workspace via team membership.

    A user has access if they are a member of any team that is assigned
    to the workspace.

    Args:
        db: Database session
        workspace_id: ID of the workspace to check
        user_id: ID of the user
        authflow: AuthFlow instance

    Returns:
        True if user has access, False otherwise

    Example:
        if check_workspace_access(db, workspace.id, user.id, authflow):
            # User can access workspace
            pass
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        return False

    # Get teams assigned to this workspace
    assigned_team_ids = [
        assignment.team_id
        for assignment in workspace.team_assignments
    ]

    if not assigned_team_ids:
        return False

    # Get user's teams in this organization
    user_teams = authflow.get_user_teams(user_id, workspace.organization_id)
    user_team_ids = [team.id for team in user_teams]

    # Check if user is in any of the assigned teams
    return bool(set(assigned_team_ids) & set(user_team_ids))


def get_user_workspaces(
    db: Session,
    user_id: UUID,
    org_id: UUID,
    authflow: Any
) -> list[Workspace]:
    """
    Get all workspaces a user can access via team membership.

    Args:
        db: Database session
        user_id: ID of the user
        org_id: ID of the organization
        authflow: AuthFlow instance

    Returns:
        List of accessible Workspaces

    Example:
        workspaces = get_user_workspaces(db, user.id, org.id, authflow)
        for workspace in workspaces:
            print(workspace.name)
    """
    # Get user's teams in this organization
    user_teams = authflow.get_user_teams(user_id, org_id)
    team_ids = [team.id for team in user_teams]

    if not team_ids:
        return []

    # Get workspaces assigned to those teams
    workspaces = (
        db.query(Workspace)
        .join(WorkspaceTeam)
        .filter(
            Workspace.organization_id == org_id,
            WorkspaceTeam.team_id.in_(team_ids)
        )
        .distinct()
        .all()
    )

    return workspaces


def get_user_workspace_role(
    db: Session,
    workspace_id: UUID,
    user_id: UUID,
    authflow: Any
) -> str | None:
    """
    Get the effective role of a user in a workspace.

    Returns the highest role from all teams the user belongs to
    that are assigned to this workspace.

    Args:
        db: Database session
        workspace_id: ID of the workspace
        user_id: ID of the user
        authflow: AuthFlow instance

    Returns:
        The user's role in the workspace, or None if no access

    Example:
        role = get_user_workspace_role(db, workspace.id, user.id, authflow)
        if role == "admin":
            # User is admin of this workspace
            pass
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        return None

    # Get user's teams
    user_teams = authflow.get_user_teams(user_id, workspace.organization_id)
    user_team_ids = [team.id for team in user_teams]

    if not user_team_ids:
        return None

    # Get team assignments for this workspace
    assignments = (
        db.query(WorkspaceTeam)
        .filter(
            WorkspaceTeam.workspace_id == workspace_id,
            WorkspaceTeam.team_id.in_(user_team_ids)
        )
        .all()
    )

    if not assignments:
        return None

    # Role hierarchy: admin > contributor > viewer
    role_priority = {"admin": 3, "contributor": 2, "viewer": 1}

    highest_role = None
    highest_priority = 0

    for assignment in assignments:
        if assignment.role:
            priority = role_priority.get(assignment.role, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_role = assignment.role

    return highest_role
