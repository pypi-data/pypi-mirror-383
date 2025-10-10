"""Workspace middleware for FastAPI"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class WorkspaceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and store workspace context from X-Workspace-ID header.

    This middleware extracts the X-Workspace-ID header from incoming requests
    and stores it in request.state for easy access throughout the request lifecycle.

    The workspace ID is NOT validated here - validation happens in the
    get_current_workspace() dependency.

    Example:
        from fastapi import FastAPI
        from workspaceflow.core.middleware import WorkspaceMiddleware

        app = FastAPI()
        app.add_middleware(WorkspaceMiddleware)

        @app.get("/data")
        async def get_data(request: Request):
            workspace_id = request.state.workspace_id  # Available if header present
            return {"workspace_id": workspace_id}
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Process request and extract workspace context"""

        # Extract workspace ID from header
        workspace_id = request.headers.get("X-Workspace-ID")

        # Store in request state (can be None)
        request.state.workspace_id = workspace_id

        # Continue processing request
        response = await call_next(request)

        # Optionally add workspace ID to response headers for debugging
        if workspace_id:
            response.headers["X-Workspace-Context"] = workspace_id

        return response
