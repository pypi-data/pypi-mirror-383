"""Role-Based Access Control (RBAC) utilities for FastAPI services."""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, Optional, Set

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class Permission:
    """Permission representation."""

    def __init__(self, resource: str, action: str):
        """Initialize permission.

        Args:
            resource: Resource type (e.g., 'events', 'playbooks', 'clusters')
            action: Action type (e.g., 'read', 'write', 'delete', 'execute')
        """
        self.resource = resource
        self.action = action
        self.name = f"{resource}:{action}"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Permission({self.name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Permission):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __hash__(self) -> int:
        return hash(self.name)


class Role:
    """Role with associated permissions."""

    def __init__(self, name: str, permissions: Set[str] | None = None, description: str = ""):
        """Initialize role.

        Args:
            name: Role name
            permissions: Set of permission strings (e.g., {'events:read', 'playbooks:write'})
            description: Role description
        """
        self.name = name
        self.permissions = permissions or set()
        self.description = description

    def has_permission(self, permission: str | Permission) -> bool:
        """Check if role has permission.

        Args:
            permission: Permission string or Permission object

        Returns:
            True if role has permission or wildcard
        """
        perm_str = str(permission)
        return "*" in self.permissions or perm_str in self.permissions

    def add_permission(self, permission: str | Permission) -> None:
        """Add permission to role.

        Args:
            permission: Permission string or Permission object
        """
        self.permissions.add(str(permission))

    def remove_permission(self, permission: str | Permission) -> None:
        """Remove permission from role.

        Args:
            permission: Permission string or Permission object
        """
        self.permissions.discard(str(permission))


class RBACConfig:
    """RBAC configuration with roles and permissions."""

    def __init__(self):
        """Initialize RBAC configuration."""
        self.roles: Dict[str, Role] = {}
        self._setup_default_roles()

    def _setup_default_roles(self) -> None:
        """Setup default KubeMind roles."""
        self.roles = {
            "admin": Role(
                "admin",
                {"*"},
                "Full system access"
            ),
            "operator": Role(
                "operator",
                {
                    "events:read", "events:write",
                    "playbooks:read", "playbooks:write", "playbooks:execute",
                    "investigations:read", "investigations:write",
                    "clusters:read", "clusters:write",
                    "alerts:read", "alerts:write",
                    "executions:read"
                },
                "Operational access to manage incidents and playbooks"
            ),
            "developer": Role(
                "developer",
                {
                    "playbooks:read", "playbooks:write",
                    "events:read",
                    "executions:read",
                    "clusters:read"
                },
                "Development access to create and test playbooks"
            ),
            "viewer": Role(
                "viewer",
                {
                    "events:read",
                    "playbooks:read",
                    "investigations:read",
                    "clusters:read",
                    "executions:read"
                },
                "Read-only access"
            ),
        }

    def get_role(self, role_name: str) -> Role | None:
        """Get role by name.

        Args:
            role_name: Role name

        Returns:
            Role object or None if not found
        """
        return self.roles.get(role_name.lower())

    def add_role(self, role: Role) -> None:
        """Add or update role.

        Args:
            role: Role object
        """
        self.roles[role.name.lower()] = role

    def has_permission(self, role_name: str, permission: str | Permission) -> bool:
        """Check if role has permission.

        Args:
            role_name: Role name
            permission: Permission string or Permission object

        Returns:
            True if role has permission
        """
        role = self.get_role(role_name)
        if not role:
            return False
        return role.has_permission(permission)


# Global RBAC configuration instance
_rbac_config: RBACConfig | None = None


def get_rbac_config() -> RBACConfig:
    """Get global RBAC configuration.

    Returns:
        RBACConfig instance
    """
    global _rbac_config
    if _rbac_config is None:
        _rbac_config = RBACConfig()
    return _rbac_config


def configure_rbac(roles: Dict[str, Dict[str, Any]]) -> None:
    """Configure RBAC with custom roles.

    Args:
        roles: Dictionary of role_name -> {permissions: [...], description: "..."}

    Example:
        configure_rbac({
            "custom_role": {
                "permissions": ["events:read", "playbooks:write"],
                "description": "Custom role"
            }
        })
    """
    global _rbac_config
    config = get_rbac_config()

    for role_name, role_data in roles.items():
        role = Role(
            name=role_name,
            permissions=set(role_data.get("permissions", [])),
            description=role_data.get("description", "")
        )
        config.add_role(role)


class PermissionChecker:
    """Permission checker for verifying user permissions."""

    def __init__(self, config: RBACConfig | None = None):
        """Initialize permission checker.

        Args:
            config: RBAC configuration (uses global config if not provided)
        """
        self.config = config or get_rbac_config()

    def check(
        self,
        user_role: str,
        required_permissions: Iterable[str],
        require_all: bool = True
    ) -> bool:
        """Check if user role has required permissions.

        Args:
            user_role: User's role name
            required_permissions: List of required permission strings
            require_all: If True, all permissions required; if False, any permission sufficient

        Returns:
            True if permissions satisfied
        """
        role = self.config.get_role(user_role)
        if not role:
            return False

        perms = list(required_permissions)
        if require_all:
            return all(role.has_permission(p) for p in perms)
        else:
            return any(role.has_permission(p) for p in perms)

    def enforce(
        self,
        user_role: str,
        required_permissions: Iterable[str],
        require_all: bool = True,
        error_message: str = "Insufficient permissions"
    ) -> None:
        """Enforce permission check, raise exception if failed.

        Args:
            user_role: User's role name
            required_permissions: List of required permission strings
            require_all: If True, all permissions required; if False, any permission sufficient
            error_message: Error message for exception

        Raises:
            HTTPException: If permission check fails
        """
        if not self.check(user_role, required_permissions, require_all):
            logger.warning(
                f"Permission denied for role '{user_role}': {list(required_permissions)}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message
            )


def create_permission_dependency(*required_permissions: str, require_all: bool = True) -> Callable:
    """Create FastAPI dependency for permission checking.

    Args:
        *required_permissions: Required permission strings
        require_all: If True, all permissions required; if False, any permission sufficient

    Returns:
        FastAPI dependency function

    Example:
        from fastapi import Depends
        from kubemind_common.security.rbac import create_permission_dependency

        @app.get("/playbooks")
        async def list_playbooks(
            user: User = Depends(create_permission_dependency("playbooks:read"))
        ):
            ...
    """
    def dependency(user: Any) -> Any:
        """Permission check dependency.

        Args:
            user: User object (must have 'role' attribute)

        Returns:
            User object if permission check passes

        Raises:
            HTTPException: If permission check fails
        """
        if not hasattr(user, "role"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User object missing 'role' attribute"
            )

        checker = PermissionChecker()
        checker.enforce(
            user_role=user.role or "viewer",
            required_permissions=required_permissions,
            require_all=require_all,
            error_message=f"Forbidden: requires {', '.join(required_permissions)}"
        )
        return user

    return dependency


def create_role_dependency(*allowed_roles: str) -> Callable:
    """Create FastAPI dependency for role checking.

    Args:
        *allowed_roles: Allowed role names

    Returns:
        FastAPI dependency function

    Example:
        from fastapi import Depends
        from kubemind_common.security.rbac import create_role_dependency

        @app.delete("/clusters/{id}")
        async def delete_cluster(
            cluster_id: str,
            user: User = Depends(create_role_dependency("admin", "operator"))
        ):
            ...
    """
    def dependency(user: Any) -> Any:
        """Role check dependency.

        Args:
            user: User object (must have 'role' attribute)

        Returns:
            User object if role check passes

        Raises:
            HTTPException: If role check fails
        """
        if not hasattr(user, "role"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User object missing 'role' attribute"
            )

        user_role = (user.role or "viewer").lower()

        if user_role not in [r.lower() for r in allowed_roles] and user_role != "admin":
            logger.warning(
                f"Role denied for user role '{user_role}': allowed roles {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: requires one of roles {', '.join(allowed_roles)}"
            )

        return user

    return dependency
