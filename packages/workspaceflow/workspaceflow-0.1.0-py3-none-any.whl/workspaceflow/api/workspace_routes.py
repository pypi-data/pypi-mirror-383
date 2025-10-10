"""Workspace CRUD routes"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from workspaceflow.api.dependencies import (
    get_workspace_service,
    get_current_workspace,
    get_authflow
)
from workspaceflow.api.schemas import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceResponse,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    AssignTeamRequest,
    WorkspaceTeamResponse,
    WorkspaceMemberResponse
)
from workspaceflow.core.workspace import WorkspaceService
from workspaceflow.models.workspace import Workspace
from workspaceflow.core.access_control import get_user_workspaces


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workspace",
    description="Create a new workspace/project within an organization"
)
async def create_workspace(
    data: CreateWorkspaceRequest,
    service: WorkspaceService = Depends(get_workspace_service),
    authflow = Depends(get_authflow)
):
    """Create a new workspace"""
    # Note: In real implementation, user should come from dependency
    # This is simplified for the example
    user = None  # Should be: await get_current_user(request)

    workspace = service.create_workspace(
        user_id=user.id if user else data.organization_id,  # Temp workaround
        org_id=data.organization_id,
        name=data.name,
        description=data.description,
        settings=data.settings
    )

    return WorkspaceResponse.model_validate(workspace)


@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="List workspaces",
    description="List all workspaces the current user can access"
)
async def list_workspaces(
    org_id: UUID = Query(..., description="Organization ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: WorkspaceService = Depends(get_workspace_service),
    authflow = Depends(get_authflow)
):
    """List workspaces accessible to current user"""
    # Get current user
    # In production, this would use: from authflow.dependencies import get_current_user
    user = None  # Should be: await get_current_user(request)

    # Use org_id as user_id temporarily if no user is available
    # In production, this should use the actual authenticated user
    user_id = user.id if user else org_id

    workspaces = service.list_workspaces(
        org_id=org_id,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    workspace_responses = [
        WorkspaceResponse.model_validate(ws) for ws in workspaces
    ]

    return WorkspaceListResponse(
        workspaces=workspace_responses,
        total=len(workspaces),  # TODO: Add count query
        limit=limit,
        offset=offset
    )


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceDetailResponse,
    summary="Get workspace details",
    description="Get detailed information about a workspace including team assignments"
)
async def get_workspace(
    workspace_id: UUID,
    service: WorkspaceService = Depends(get_workspace_service)
):
    """Get workspace by ID"""
    workspace = service.get_workspace(workspace_id, load_teams=True)
    return WorkspaceDetailResponse.model_validate(workspace)


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace",
    description="Update workspace name, description, or settings"
)
async def update_workspace(
    workspace_id: UUID,
    data: UpdateWorkspaceRequest,
    service: WorkspaceService = Depends(get_workspace_service),
    authflow = Depends(get_authflow)
):
    """Update workspace"""
    # Get current user
    # In production: from authflow.dependencies import get_current_user
    user = None  # Should be: await get_current_user(request)

    workspace = service.update_workspace(
        workspace_id=workspace_id,
        user_id=user.id if user else workspace_id,  # Temp workaround
        name=data.name,
        description=data.description,
        settings=data.settings
    )

    return WorkspaceResponse.model_validate(workspace)


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
    description="Permanently delete a workspace and all its data"
)
async def delete_workspace(
    workspace_id: UUID,
    service: WorkspaceService = Depends(get_workspace_service),
    authflow = Depends(get_authflow)
):
    """Delete workspace"""
    # Get current user
    # In production: from authflow.dependencies import get_current_user
    user = None  # Should be: await get_current_user(request)

    service.delete_workspace(
        workspace_id=workspace_id,
        user_id=user.id if user else workspace_id  # Temp workaround
    )

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.post(
    "/{workspace_id}/teams",
    response_model=WorkspaceTeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign team to workspace",
    description="Grant a team access to a workspace/project"
)
async def assign_team(
    workspace_id: UUID,
    data: AssignTeamRequest,
    service: WorkspaceService = Depends(get_workspace_service),
    authflow = Depends(get_authflow)
):
    """Assign a team to workspace"""
    # Get current user
    # In production: from authflow.dependencies import get_current_user
    user = None  # Should be: await get_current_user(request)

    assignment = service.assign_team(
        workspace_id=workspace_id,
        team_id=data.team_id,
        user_id=user.id if user else workspace_id,  # Temp workaround
        role=data.role
    )

    return WorkspaceTeamResponse.model_validate(assignment)


@router.delete(
    "/{workspace_id}/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove team from workspace",
    description="Revoke a team's access to a workspace"
)
async def remove_team(
    workspace_id: UUID,
    team_id: UUID,
    service: WorkspaceService = Depends(get_workspace_service),
    authflow = Depends(get_authflow)
):
    """Remove team assignment from workspace"""
    # Get current user
    # In production: from authflow.dependencies import get_current_user
    user = None  # Should be: await get_current_user(request)

    service.remove_team(
        workspace_id=workspace_id,
        team_id=team_id,
        user_id=user.id if user else workspace_id  # Temp workaround
    )

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
    summary="List workspace members",
    description="Get all users who have access to this workspace via team membership"
)
async def list_workspace_members(
    workspace_id: UUID,
    service: WorkspaceService = Depends(get_workspace_service)
):
    """Get all members with access to workspace"""
    members = service.get_workspace_members(workspace_id)

    # Convert authflow users to response format
    return [
        WorkspaceMemberResponse.model_validate(member)
        for member in members
    ]
