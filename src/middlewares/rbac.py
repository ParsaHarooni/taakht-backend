"""RBAC (Role-Based Access Control) middleware for Taakht backend.

This module provides RBAC middleware and dependencies for FastAPI,
including permission checking decorators and resource ownership validation.
"""

import logging
from functools import wraps
from typing import Callable, List

from fastapi import Depends, HTTPException, status

from src.middlewares.auth import get_current_active_user
from src.models.user import User
from src.services.rbac import RBACService

logger = logging.getLogger(__name__)


def require_permission(permission: str):
    """Decorator to require a specific permission for a route."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args, current_user: User = Depends(get_current_active_user), **kwargs
        ):
            has_perm = await RBACService.has_permission(current_user.id, permission)
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission} required",
                )
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


def require_any_permission(permissions: List[str]):
    """Decorator to require any of the specified permissions for a route."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args, current_user: User = Depends(get_current_active_user), **kwargs
        ):
            has_perm = await RBACService.has_any_permission(
                current_user.id, permissions
            )
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: one of {permissions} required",
                )
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


def require_all_permissions(permissions: List[str]):
    """Decorator to require all of the specified permissions for a route."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args, current_user: User = Depends(get_current_active_user), **kwargs
        ):
            has_perm = await RBACService.has_all_permissions(
                current_user.id, permissions
            )
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: all of {permissions} required",
                )
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


def get_user_with_permission(permission: str):
    """Dependency to get current user with a specific permission."""

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        has_perm = await RBACService.has_permission(current_user.id, permission)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required",
            )
        return current_user

    return dependency


def get_user_with_any_permission(permissions: List[str]):
    """Dependency to get current user with any of the specified permissions."""

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        has_perm = await RBACService.has_any_permission(current_user.id, permissions)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: one of {permissions} required",
            )
        return current_user

    return dependency


def get_user_with_all_permissions(permissions: List[str]):
    """Dependency to get current user with all of the specified permissions."""

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        has_perm = await RBACService.has_all_permissions(current_user.id, permissions)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: all of {permissions} required",
            )
        return current_user

    return dependency


# Predefined permission dependencies for common operations
def require_user_manage():
    """Require user management permission."""
    return get_user_with_permission("user:manage")


def require_item_manage():
    """Require item management permission."""
    return get_user_with_permission("item:manage")


def require_trade_manage():
    """Require trade management permission."""
    return get_user_with_permission("trade:manage")


def require_category_manage():
    """Require category management permission."""
    return get_user_with_permission("category:manage")


def require_system_admin():
    """Require system admin permission."""
    return get_user_with_permission("system:admin")


def require_moderation_permission():
    """Require any moderation permission."""
    return get_user_with_any_permission(
        ["moderate:users", "moderate:items", "moderate:trades", "moderate:content"]
    )


# Resource ownership checking
def check_resource_ownership():
    """Check if current user owns the resource or has management permission."""

    async def dependency(
        resource_user_id: int, current_user: User = Depends(get_current_active_user)
    ) -> User:
        # User owns the resource
        if current_user.id == resource_user_id:
            return current_user

        # User has management permission
        has_manage_perm = await RBACService.has_any_permission(
            current_user.id,
            ["user:manage", "item:manage", "trade:manage", "category:manage"],
        )

        if has_manage_perm:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you don't own this resource and lack management permissions",
        )

    return dependency


# Role-based access control helpers
class RBACMiddleware:
    """RBAC middleware class for advanced permission checking."""

    @staticmethod
    async def check_permission(user_id: int, permission: str) -> bool:
        """Check if user has a specific permission."""
        return await RBACService.has_permission(user_id, permission)

    @staticmethod
    async def check_permissions(
        user_id: int, permissions: List[str], require_all: bool = False
    ) -> bool:
        """Check if user has permissions."""
        if require_all:
            return await RBACService.has_all_permissions(user_id, permissions)

        return await RBACService.has_any_permission(user_id, permissions)

    @staticmethod
    async def get_user_permissions(user_id: int) -> List[str]:
        """Get all permissions for a user."""
        permissions = await RBACService.get_user_permissions(user_id)
        return list(permissions)

    @staticmethod
    async def get_user_roles(user_id: int):
        """Get all roles for a user."""
        return await RBACService.get_user_roles(user_id)
