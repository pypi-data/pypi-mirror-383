"""
Workspaceflow - Pluggable workspace management for Python web applications

A complete workspace/project management system that integrates with authflow
for authentication and team-based access control.

Example:
    from fastapi import FastAPI
    from authflow import setup_auth
    from workspaceflow import setup_workspaces

    app = FastAPI()

    # Setup authentication
    authflow = setup_auth(app, preset="multi_tenant")

    # Setup workspace management
    setup_workspaces(app, authflow=authflow)
"""

__version__ = "0.1.0"

from workspaceflow.models.workspace import Workspace
from workspaceflow.models.workspace_team import WorkspaceTeam
from workspaceflow.models.mixins import WorkspaceScopedMixin
from workspaceflow.core.workspace import WorkspaceService
from workspaceflow.core.access_control import (
    check_workspace_access,
    get_user_workspaces,
    get_user_workspace_role
)
from workspaceflow.config import WorkspaceConfig
from workspaceflow.setup import setup_workspaces

__all__ = [
    "Workspace",
    "WorkspaceTeam",
    "WorkspaceScopedMixin",
    "WorkspaceService",
    "check_workspace_access",
    "get_user_workspaces",
    "get_user_workspace_role",
    "WorkspaceConfig",
    "setup_workspaces",
]
