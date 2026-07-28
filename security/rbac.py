"""
BLACK VEIL V2 — Role-Based Access Control (RBAC)
Permission management with decorators for FastAPI endpoints
"""
from enum import Enum
from functools import wraps
from typing import Callable, Optional

from fastapi import HTTPException, status


class Permission(str, Enum):
    """Granular permissions available in the system"""

    READ_TRUST = "read:trust"
    WRITE_TRUST = "write:trust"
    UPDATE_TRUST_WEIGHTS = "update:trust_weights"
    READ_THREAT = "read:threat"
    WRITE_THREAT = "write:threat"
    READ_DECEPTION = "read:deception"
    WRITE_DECEPTION = "write:deception"
    DEPLOY_DECEPTION = "deploy:deception"
    READ_RESPONSE = "read:response"
    EXECUTE_RESPONSE = "execute:response"
    READ_AGENTS = "read:agents"
    WRITE_AGENTS = "write:agents"
    REGISTER_AGENTS = "register:agents"
    READ_REPORTS = "read:reports"
    GENERATE_REPORTS = "generate:reports"
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"


class Role(str, Enum):
    """Predefined roles with associated permission sets"""

    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    AGENT = "agent"
    VIEWER = "viewer"


ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.ADMIN: [
        Permission.ADMIN_READ, Permission.ADMIN_WRITE, Permission.ADMIN_USERS,
        Permission.ADMIN_SYSTEM, Permission.READ_TRUST, Permission.WRITE_TRUST,
        Permission.UPDATE_TRUST_WEIGHTS, Permission.READ_THREAT, Permission.WRITE_THREAT,
        Permission.READ_DECEPTION, Permission.WRITE_DECEPTION, Permission.DEPLOY_DECEPTION,
        Permission.READ_RESPONSE, Permission.EXECUTE_RESPONSE, Permission.READ_AGENTS,
        Permission.WRITE_AGENTS, Permission.REGISTER_AGENTS, Permission.READ_REPORTS,
        Permission.GENERATE_REPORTS,
    ],
    Role.OPERATOR: [
        Permission.READ_TRUST, Permission.WRITE_TRUST, Permission.READ_THREAT,
        Permission.READ_DECEPTION, Permission.WRITE_DECEPTION, Permission.DEPLOY_DECEPTION,
        Permission.READ_RESPONSE, Permission.EXECUTE_RESPONSE, Permission.READ_AGENTS,
        Permission.READ_REPORTS,
    ],
    Role.ANALYST: [
        Permission.READ_TRUST, Permission.READ_THREAT, Permission.READ_DECEPTION,
        Permission.READ_RESPONSE, Permission.READ_AGENTS, Permission.READ_REPORTS,
        Permission.GENERATE_REPORTS,
    ],
    Role.AGENT: [
        Permission.WRITE_TRUST, Permission.WRITE_THREAT,
    ],
    Role.VIEWER: [
        Permission.READ_TRUST, Permission.READ_THREAT, Permission.READ_DECEPTION,
        Permission.READ_AGENTS, Permission.READ_REPORTS,
    ],
}


class RBACManager:
    """Role-Based Access Control Manager."""

    @staticmethod
    def get_permissions_for_role(role: Role) -> list[Permission]:
        return ROLE_PERMISSIONS.get(role, [])

    @staticmethod
    def has_permission(user_permissions: list[str], required_permission: Permission) -> bool:
        return required_permission.value in user_permissions

    @staticmethod
    def has_any_permission(user_permissions: list[str], required_permissions: list[Permission]) -> bool:
        perm_values = {p.value for p in required_permissions}
        return bool(perm_values & set(user_permissions))

    @staticmethod
    def has_all_permissions(user_permissions: list[str], required_permissions: list[Permission]) -> bool:
        perm_values = {p.value for p in required_permissions}
        return perm_values.issubset(set(user_permissions))


def require_permission(*permissions: Permission) -> Callable:
    """Decorator: Require specific permissions for a FastAPI endpoint."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            user_permissions = current_user.get("permissions", [])
            if not RBACManager.has_all_permissions(user_permissions, list(permissions)):
                missing = [p.value for p in permissions if p.value not in user_permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(missing)}",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role) -> Callable:
    """Decorator: Require a specific role for a FastAPI endpoint."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            user_role = current_user.get("role", "")
            if user_role != role.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role: {role.value}. Your role: {user_role}",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


rbac_manager = RBACManager()
