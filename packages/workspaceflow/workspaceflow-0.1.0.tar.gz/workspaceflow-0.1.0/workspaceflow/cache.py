"""
Redis cache manager for workspace data

Provides caching for frequently accessed workspace data to reduce database load.
"""

import json
from typing import Any, Optional
from datetime import timedelta

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = Any  # Type hint fallback


class WorkspaceCache:
    """
    Redis-based cache manager for workspace data

    Caches:
    - Workspace details
    - Team membership lookups
    - Access control decisions

    Usage:
        cache = WorkspaceCache(redis_url="redis://localhost:6379/0")

        # Cache workspace
        cache.set_workspace(workspace_id, workspace_data)

        # Get cached workspace
        workspace = cache.get_workspace(workspace_id)

        # Cache team membership
        cache.set_user_workspaces(user_id, workspace_ids)
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        prefix: str = "workspaceflow:",
        default_ttl: int = 3600  # 1 hour
    ):
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is required for caching. "
                "Install it with: pip install redis"
            )

        self.client: Redis = redis.from_url(redis_url, decode_responses=True)
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _key(self, *parts: str) -> str:
        """Generate cache key with prefix"""
        return self.prefix + ":".join(parts)

    # Workspace caching

    def get_workspace(self, workspace_id: str) -> Optional[dict]:
        """Get cached workspace data"""
        key = self._key("workspace", workspace_id)
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set_workspace(
        self,
        workspace_id: str,
        workspace_data: dict,
        ttl: Optional[int] = None
    ) -> None:
        """Cache workspace data"""
        key = self._key("workspace", workspace_id)
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(workspace_data)
        )

    def delete_workspace(self, workspace_id: str) -> None:
        """Remove workspace from cache"""
        key = self._key("workspace", workspace_id)
        self.client.delete(key)

    # User workspace membership caching

    def get_user_workspaces(self, user_id: str) -> Optional[list[str]]:
        """Get cached list of workspace IDs user has access to"""
        key = self._key("user_workspaces", user_id)
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set_user_workspaces(
        self,
        user_id: str,
        workspace_ids: list[str],
        ttl: Optional[int] = None
    ) -> None:
        """Cache user's workspace access"""
        key = self._key("user_workspaces", user_id)
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(workspace_ids)
        )

    def delete_user_workspaces(self, user_id: str) -> None:
        """Remove user's workspace cache"""
        key = self._key("user_workspaces", user_id)
        self.client.delete(key)

    # Team assignment caching

    def get_workspace_teams(self, workspace_id: str) -> Optional[list[str]]:
        """Get cached list of team IDs assigned to workspace"""
        key = self._key("workspace_teams", workspace_id)
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set_workspace_teams(
        self,
        workspace_id: str,
        team_ids: list[str],
        ttl: Optional[int] = None
    ) -> None:
        """Cache workspace's team assignments"""
        key = self._key("workspace_teams", workspace_id)
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(team_ids)
        )

    def delete_workspace_teams(self, workspace_id: str) -> None:
        """Remove workspace teams cache"""
        key = self._key("workspace_teams", workspace_id)
        self.client.delete(key)

    # Access control caching

    def get_access_decision(
        self,
        user_id: str,
        workspace_id: str
    ) -> Optional[bool]:
        """Get cached access control decision"""
        key = self._key("access", user_id, workspace_id)
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set_access_decision(
        self,
        user_id: str,
        workspace_id: str,
        has_access: bool,
        ttl: Optional[int] = None
    ) -> None:
        """Cache access control decision"""
        key = self._key("access", user_id, workspace_id)
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(has_access)
        )

    def delete_access_decision(
        self,
        user_id: str,
        workspace_id: str
    ) -> None:
        """Remove access decision cache"""
        key = self._key("access", user_id, workspace_id)
        self.client.delete(key)

    # Bulk invalidation

    def invalidate_workspace(self, workspace_id: str) -> None:
        """
        Invalidate all cache entries related to a workspace

        This should be called when:
        - Workspace is updated or deleted
        - Team assignments change
        """
        # Delete workspace data
        self.delete_workspace(workspace_id)
        self.delete_workspace_teams(workspace_id)

        # Delete all access decisions for this workspace
        pattern = self._key("access", "*", workspace_id)
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

    def invalidate_user(self, user_id: str) -> None:
        """
        Invalidate all cache entries related to a user

        This should be called when:
        - User's team membership changes
        - User is deleted
        """
        # Delete user workspace list
        self.delete_user_workspaces(user_id)

        # Delete all access decisions for this user
        pattern = self._key("access", user_id, "*")
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

    def clear_all(self) -> None:
        """Clear all workspaceflow cache entries"""
        pattern = self._key("*")
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            return self.client.ping()
        except Exception:
            return False


class NoOpCache:
    """
    No-operation cache for when Redis is not available

    This allows the application to work without caching
    """

    def get_workspace(self, workspace_id: str) -> None:
        return None

    def set_workspace(self, workspace_id: str, workspace_data: dict, ttl: int = None) -> None:
        pass

    def delete_workspace(self, workspace_id: str) -> None:
        pass

    def get_user_workspaces(self, user_id: str) -> None:
        return None

    def set_user_workspaces(self, user_id: str, workspace_ids: list, ttl: int = None) -> None:
        pass

    def delete_user_workspaces(self, user_id: str) -> None:
        pass

    def get_workspace_teams(self, workspace_id: str) -> None:
        return None

    def set_workspace_teams(self, workspace_id: str, team_ids: list, ttl: int = None) -> None:
        pass

    def delete_workspace_teams(self, workspace_id: str) -> None:
        pass

    def get_access_decision(self, user_id: str, workspace_id: str) -> None:
        return None

    def set_access_decision(self, user_id: str, workspace_id: str, has_access: bool, ttl: int = None) -> None:
        pass

    def delete_access_decision(self, user_id: str, workspace_id: str) -> None:
        pass

    def invalidate_workspace(self, workspace_id: str) -> None:
        pass

    def invalidate_user(self, user_id: str) -> None:
        pass

    def clear_all(self) -> None:
        pass

    def health_check(self) -> bool:
        return True
