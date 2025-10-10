"""Setup function for integrating workspaceflow with FastAPI"""

from typing import Any, Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from workspaceflow.config import WorkspaceConfig
from workspaceflow.api.workspace_routes import router as workspace_router
from workspaceflow.core.middleware import WorkspaceMiddleware
from workspaceflow.exceptions import WorkspaceFlowException


def setup_workspaces(
    app: FastAPI,
    authflow: Any,
    config: WorkspaceConfig | None = None,
    prefix: str = "/api/v1/workspaces",
    db_session_factory: Callable[[], Session] | None = None
) -> None:
    """
    Setup workspaceflow integration with FastAPI application.

    This function:
    1. Registers workspace routes
    2. Adds workspace middleware
    3. Sets up exception handlers
    4. Stores authflow and config in app state

    Args:
        app: FastAPI application instance
        authflow: AuthFlow instance for authentication and authorization
        config: WorkspaceConfig (optional, will create default if not provided)
        prefix: URL prefix for workspace routes (default: /api/v1/workspaces)
        db_session_factory: Database session factory (optional)

    Example:
        from fastapi import FastAPI
        from authflow import setup_auth
        from workspaceflow import setup_workspaces

        app = FastAPI()

        # Setup authflow first
        authflow = setup_auth(app, preset="multi_tenant")

        # Setup workspaceflow
        setup_workspaces(app, authflow=authflow)

        # Now you have:
        # - Auth routes: /api/v1/auth/*
        # - Workspace routes: /api/v1/workspaces/*
    """
    # Use provided config or create default
    if config is None:
        config = WorkspaceConfig()

    # Store authflow and config in app state
    app.state.authflow = authflow
    app.state.workspace_config = config

    # Setup database session factory if provided
    if db_session_factory:
        app.state.db = db_session_factory
    elif config.database_url:
        # Create default session factory from config
        engine = create_engine(
            config.database_url,
            echo=config.database_echo
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        app.state.db = SessionLocal

    # Add workspace middleware (if enabled)
    if config.enable_workspace_middleware:
        app.add_middleware(WorkspaceMiddleware)

    # Register workspace routes
    app.include_router(workspace_router, prefix=prefix)

    # Add exception handlers for workspaceflow exceptions
    @app.exception_handler(WorkspaceFlowException)
    async def workspaceflow_exception_handler(
        request: Request,
        exc: WorkspaceFlowException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    # Log successful setup
    print(f"✓ WorkspaceFlow initialized at {prefix}")
    print(f"  - Middleware: {'enabled' if config.enable_workspace_middleware else 'disabled'}")
    print(f"  - Caching: {'enabled' if config.enable_caching else 'disabled'}")
