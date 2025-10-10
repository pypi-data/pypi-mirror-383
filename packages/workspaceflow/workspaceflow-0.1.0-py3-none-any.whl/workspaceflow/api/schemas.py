"""Pydantic schemas for request and response validation"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Request Schemas

class CreateWorkspaceRequest(BaseModel):
    """Request schema for creating a workspace"""

    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    organization_id: UUID = Field(..., description="Organization ID")
    description: str | None = Field(None, max_length=1000, description="Workspace description")
    settings: dict = Field(default_factory=dict, description="Workspace settings")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Project Alpha",
                    "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                    "description": "Our main project for 2024",
                    "settings": {"theme": "dark"}
                }
            ]
        }
    }


class UpdateWorkspaceRequest(BaseModel):
    """Request schema for updating a workspace"""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    settings: dict | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Project Alpha v2",
                    "description": "Updated description"
                }
            ]
        }
    }


class AssignTeamRequest(BaseModel):
    """Request schema for assigning a team to a workspace"""

    team_id: UUID = Field(..., description="Team ID to assign")
    role: str | None = Field(None, description="Optional project-specific role")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        if v is not None:
            allowed_roles = ["admin", "contributor", "viewer"]
            if v not in allowed_roles:
                raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "team_id": "123e4567-e89b-12d3-a456-426614174001",
                    "role": "admin"
                }
            ]
        }
    }


# Response Schemas

class WorkspaceTeamResponse(BaseModel):
    """Response schema for workspace team assignment"""

    id: UUID
    workspace_id: UUID
    team_id: UUID
    role: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceResponse(BaseModel):
    """Response schema for workspace"""

    id: UUID
    name: str
    slug: str
    description: str | None
    organization_id: UUID
    settings: dict
    created_at: datetime
    updated_at: datetime

    # Optional: computed fields
    team_count: int | None = Field(None, description="Number of assigned teams")

    model_config = {"from_attributes": True}


class WorkspaceDetailResponse(WorkspaceResponse):
    """Detailed response schema for workspace including team assignments"""

    team_assignments: list[WorkspaceTeamResponse] = []

    model_config = {"from_attributes": True}


class WorkspaceListResponse(BaseModel):
    """Response schema for list of workspaces with pagination"""

    workspaces: list[WorkspaceResponse]
    total: int
    limit: int
    offset: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "workspaces": [],
                    "total": 0,
                    "limit": 100,
                    "offset": 0
                }
            ]
        }
    }


class WorkspaceMemberResponse(BaseModel):
    """Response schema for workspace member (from authflow)"""

    id: UUID
    email: str
    username: str | None = None
    full_name: str | None = None

    # Team membership info
    teams: list[str] = Field(default_factory=list, description="Team names user belongs to")

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Response schema for errors"""

    detail: str
    status_code: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Workspace not found",
                    "status_code": 404
                }
            ]
        }
    }
