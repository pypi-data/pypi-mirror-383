"""FastAPI dependencies for workspace management"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from workspaceflow.models.workspace import Workspace
from workspaceflow.core.workspace import WorkspaceService
from workspaceflow.core.access_control import check_workspace_access
from workspaceflow.exceptions import (
    InvalidWorkspaceHeaderError,
    WorkspaceNotFoundError,
    WorkspaceAccessDeniedError
)
from workspaceflow.config import WorkspaceConfig


def get_config() -> WorkspaceConfig:
    """Get workspaceflow configuration"""
    return WorkspaceConfig()


def get_db(request: Request) -> Session:
    """
    Get database session from request state.

    This should be set up by the application using workspaceflow.
    The setup_workspaces() function will configure this.
    """
    if not hasattr(request.app.state, "db"):
        raise RuntimeError(
            "Database session not configured. "
            "Make sure to call setup_workspaces() with proper database configuration."
        )
    return request.app.state.db()


def get_authflow(request: Request):
    """
    Get authflow instance from request state.

    The authflow instance should be stored in app.state.authflow
    by the setup_workspaces() function.
    """
    if not hasattr(request.app.state, "authflow"):
        raise RuntimeError(
            "AuthFlow instance not configured. "
            "Make sure to pass authflow instance to setup_workspaces()."
        )
    return request.app.state.authflow


def get_workspace_service(
    db: Session = Depends(get_db),
    authflow = Depends(get_authflow),
    config: WorkspaceConfig = Depends(get_config)
) -> WorkspaceService:
    """Get workspace service instance"""
    return WorkspaceService(db, authflow, config)


async def get_current_workspace(
    x_workspace_id: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
    authflow = Depends(get_authflow),
    request: Request = None
) -> Workspace:
    """
    Get current workspace from X-Workspace-ID header.

    This dependency extracts the workspace ID from the request header,
    verifies the workspace exists, and checks that the current user
    has access via team membership.

    Args:
        x_workspace_id: Workspace ID from X-Workspace-ID header
        db: Database session
        authflow: AuthFlow instance
        request: FastAPI request

    Returns:
        The Workspace object

    Raises:
        InvalidWorkspaceHeaderError: If header is missing or invalid
        WorkspaceNotFoundError: If workspace doesn't exist
        WorkspaceAccessDeniedError: If user doesn't have access

    Example:
        @app.get("/contracts")
        async def list_contracts(
            workspace: Workspace = Depends(get_current_workspace)
        ):
            # workspace is validated and user has access
            return Contract.query_for_workspace(db, workspace.id).all()
    """
    if not x_workspace_id:
        raise InvalidWorkspaceHeaderError()

    try:
        workspace_id = UUID(x_workspace_id)
    except ValueError:
        raise InvalidWorkspaceHeaderError(f"Invalid workspace ID format: {x_workspace_id}")

    # Get workspace
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise WorkspaceNotFoundError(str(workspace_id))

    # Get current user from authflow
    # This assumes authflow's get_current_user dependency is available
    try:
        from authflow.dependencies import get_current_user
        user = await get_current_user(request)
    except ImportError:
        raise RuntimeError(
            "AuthFlow get_current_user dependency not available. "
            "Make sure authflow is properly installed and configured."
        )

    # Check access via team membership
    if not check_workspace_access(db, workspace_id, user.id, authflow):
        raise WorkspaceAccessDeniedError(str(workspace_id), str(user.id))

    return workspace


def get_optional_workspace(
    x_workspace_id: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
    authflow = Depends(get_authflow),
    request: Request = None
) -> Workspace | None:
    """
    Get current workspace if header is present, otherwise return None.

    This is useful for endpoints that can optionally filter by workspace.

    Example:
        @app.get("/search")
        async def search(
            q: str,
            workspace: Workspace | None = Depends(get_optional_workspace)
        ):
            # Search globally or within workspace
            if workspace:
                return search_in_workspace(q, workspace.id)
            return search_globally(q)
    """
    if not x_workspace_id:
        return None

    try:
        return get_current_workspace(x_workspace_id, db, authflow, request)
    except (InvalidWorkspaceHeaderError, WorkspaceNotFoundError, WorkspaceAccessDeniedError):
        return None
