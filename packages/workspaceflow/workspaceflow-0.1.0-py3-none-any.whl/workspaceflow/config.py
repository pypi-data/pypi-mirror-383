"""Configuration for workspaceflow using Pydantic Settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkspaceConfig(BaseSettings):
    """
    Configuration for workspaceflow package.

    All settings can be configured via environment variables with
    the prefix WORKSPACE_ (e.g., WORKSPACE_DATABASE_URL).

    Example:
        config = WorkspaceConfig(
            database_url="postgresql://user:pass@localhost/db",
            redis_url="redis://localhost:6379/0"
        )
    """

    model_config = SettingsConfigDict(
        env_prefix="WORKSPACE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database configuration
    database_url: str | None = "postgresql://localhost/workspaceflow"
    database_echo: bool = False  # Log SQL queries

    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600  # Default cache TTL in seconds

    # Workspace settings
    max_workspaces_per_org: int = 100  # Maximum workspaces per organization
    slug_max_length: int = 255

    # Feature flags
    enable_caching: bool = True
    enable_workspace_middleware: bool = True
