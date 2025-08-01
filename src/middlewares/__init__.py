"""Middleware module for Taakht backend.

This module provides various middleware components including CORS setup,
authentication middleware, and RBAC middleware.
"""

from .auth import (
    get_current_active_user,
    get_current_user,
    get_current_verified_user,
    get_optional_user,
)
from .cors import setup_cors
from .rbac import (
    RBACMiddleware,
    check_resource_ownership,
    get_user_with_all_permissions,
    get_user_with_any_permission,
    get_user_with_permission,
    require_all_permissions,
    require_any_permission,
    require_category_manage,
    require_item_manage,
    require_moderation_permission,
    require_permission,
    require_system_admin,
    require_trade_manage,
    require_user_manage,
)

__all__ = [
    "setup_cors",
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_optional_user",
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    "get_user_with_permission",
    "get_user_with_any_permission",
    "get_user_with_all_permissions",
    "require_user_manage",
    "require_item_manage",
    "require_trade_manage",
    "require_category_manage",
    "require_system_admin",
    "require_moderation_permission",
    "check_resource_ownership",
    "RBACMiddleware",
]
