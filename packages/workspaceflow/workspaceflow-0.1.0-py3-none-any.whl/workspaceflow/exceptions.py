"""Custom exceptions for workspaceflow"""


class WorkspaceFlowException(Exception):
    """Base exception for all workspaceflow errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class WorkspaceNotFoundError(WorkspaceFlowException):
    """Raised when a workspace cannot be found"""

    def __init__(self, workspace_id: str):
        super().__init__(
            message=f"Workspace with ID '{workspace_id}' not found",
            status_code=404
        )


class WorkspaceAccessDeniedError(WorkspaceFlowException):
    """Raised when a user doesn't have access to a workspace"""

    def __init__(self, workspace_id: str, user_id: str | None = None):
        message = f"Access denied to workspace '{workspace_id}'"
        if user_id:
            message += f" for user '{user_id}'"
        super().__init__(message=message, status_code=403)


class WorkspaceSlugConflictError(WorkspaceFlowException):
    """Raised when trying to create a workspace with a duplicate slug"""

    def __init__(self, slug: str):
        super().__init__(
            message=f"Workspace with slug '{slug}' already exists",
            status_code=409
        )


class TeamNotAssignedError(WorkspaceFlowException):
    """Raised when trying to access a team that isn't assigned to workspace"""

    def __init__(self, team_id: str, workspace_id: str):
        super().__init__(
            message=f"Team '{team_id}' is not assigned to workspace '{workspace_id}'",
            status_code=404
        )


class TeamAlreadyAssignedError(WorkspaceFlowException):
    """Raised when trying to assign a team that's already assigned"""

    def __init__(self, team_id: str, workspace_id: str):
        super().__init__(
            message=f"Team '{team_id}' is already assigned to workspace '{workspace_id}'",
            status_code=409
        )


class InvalidWorkspaceHeaderError(WorkspaceFlowException):
    """Raised when X-Workspace-ID header is missing or invalid"""

    def __init__(self, message: str = "X-Workspace-ID header is required"):
        super().__init__(message=message, status_code=400)


class WorkspacePermissionDeniedError(WorkspaceFlowException):
    """Raised when user lacks required permission for workspace operation"""

    def __init__(self, permission: str, workspace_id: str | None = None):
        message = f"Permission '{permission}' required"
        if workspace_id:
            message += f" for workspace '{workspace_id}'"
        super().__init__(message=message, status_code=403)
