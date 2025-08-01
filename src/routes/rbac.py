"""RBAC (Role-Based Access Control) API routes for Taakht backend.

This module provides comprehensive API endpoints for role and permission management
including role CRUD operations, user role assignments, and permission checking.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.middlewares.auth import get_current_active_user
from src.middlewares.rbac import (
    require_system_admin,
    require_user_manage,
)
from src.models.role import PermissionType
from src.models.user import User
from src.schemas.rbac import (
    PermissionCheckRequest,
    PermissionCheckResponse,
    RoleCreateRequest,
    RoleListResponse,
    RoleResponse,
    RoleUpdateRequest,
    UserPermissionsResponse,
    UserRoleAssignRequest,
    UserRoleListResponse,
    UserRoleResponse,
)
from src.services.rbac import RBACService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rbac", tags=["rbac"])


# Role Management Endpoints
@router.get("/roles", response_model=RoleListResponse)
async def list_roles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    include_deleted: bool = Query(False, description="Include deleted roles"),
    _: User = Depends(require_user_manage()),
):
    """List all roles with pagination."""
    from src.models.role import Role

    query = Role.all()
    if not include_deleted:
        query = query.filter(deleted_at__isnull=True)

    total = await query.count()
    offset = (page - 1) * per_page
    roles = await query.offset(offset).limit(per_page).order_by("-priority", "name")

    total_pages = (total + per_page - 1) // per_page

    return RoleListResponse(
        roles=[RoleResponse.model_validate(role) for role in roles],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    _: User = Depends(require_user_manage()),
):
    """Get a specific role by ID."""
    from src.models.role import Role

    role = await Role.filter(id=role_id, deleted_at__isnull=True).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return RoleResponse.model_validate(role)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreateRequest,
    current_user: User = Depends(require_system_admin()),
):
    """Create a new role."""
    role = await RBACService.create_role(role_data, current_user.id)
    return RoleResponse.model_validate(role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    current_user: User = Depends(require_system_admin()),
):
    """Update an existing role."""
    role = await RBACService.update_role(role_id, role_data, current_user.id)
    return RoleResponse.model_validate(role)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_system_admin()),
):
    """Delete a role."""
    await RBACService.delete_role(role_id, current_user.id)
    return {"message": "Role deleted successfully"}


# User Role Assignment Endpoints
@router.get("/users/{user_id}/roles", response_model=UserRoleListResponse)
async def get_user_roles(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    _: User = Depends(require_user_manage()),
):
    """Get all role assignments for a user."""
    # Check if user exists
    from src.models.user import User as UserModel

    user = await UserModel.filter(id=user_id, deleted_at__isnull=True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_roles = await RBACService.get_user_role_assignments(user_id)

    total = len(user_roles)
    offset = (page - 1) * per_page
    paginated_roles = user_roles[offset : offset + per_page]

    total_pages = (total + per_page - 1) // per_page

    return UserRoleListResponse(
        user_roles=[UserRoleResponse.model_validate(ur) for ur in paginated_roles],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post(
    "/users/{user_id}/roles",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_role_to_user(
    user_id: int,
    role_data: UserRoleAssignRequest,
    current_user: User = Depends(require_user_manage()),
):
    """Assign a role to a user."""
    user_role = await RBACService.assign_role_to_user(
        user_id=user_id,
        role_id=role_data.role_id,
        assigned_by_id=current_user.id,
        reason=role_data.reason,
        expires_at=role_data.expires_at,
    )

    # Get the full user role with related data
    from src.models.role import UserRole

    full_user_role = (
        await UserRole.filter(id=user_role.id).prefetch_related("role").first()
    )
    return UserRoleResponse.model_validate(full_user_role)


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_user_manage()),
):
    """Remove a role from a user."""
    await RBACService.remove_role_from_user(user_id, role_id, current_user.id)
    return {"message": "Role removed from user successfully"}


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: int,
    _: User = Depends(require_user_manage()),
):
    """Get all permissions for a user."""
    # Check if user exists
    from src.models.user import User as UserModel

    user = await UserModel.filter(id=user_id, deleted_at__isnull=True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    permissions = await RBACService.get_user_permissions(user_id)
    roles = await RBACService.get_user_roles(user_id)

    return UserPermissionsResponse(
        user_id=user_id,
        permissions=list(permissions),
        roles=[role.name for role in roles],
    )


@router.post(
    "/users/{user_id}/permissions/check", response_model=PermissionCheckResponse
)
async def check_user_permissions(
    user_id: int,
    check_data: PermissionCheckRequest,
    _: User = Depends(require_user_manage()),
):
    """Check if a user has specific permissions."""
    # Check if user exists
    from src.models.user import User as UserModel

    user = await UserModel.filter(id=user_id, deleted_at__isnull=True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_permissions = await RBACService.get_user_permissions(user_id)

    if check_data.require_all:
        has_permission = all(
            perm in user_permissions for perm in check_data.permissions
        )
        missing_permissions = [
            perm for perm in check_data.permissions if perm not in user_permissions
        ]
    else:
        has_permission = any(
            perm in user_permissions for perm in check_data.permissions
        )
        missing_permissions = [
            perm for perm in check_data.permissions if perm not in user_permissions
        ]

    return PermissionCheckResponse(
        has_permission=has_permission,
        missing_permissions=missing_permissions,
        user_permissions=list(user_permissions),
    )


# Role Users Endpoints
@router.get("/roles/{role_id}/users", response_model=UserRoleListResponse)
async def get_role_users(
    role_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    _: User = Depends(require_user_manage()),
):
    """Get all users assigned to a role."""
    # Check if role exists
    from src.models.role import Role

    role = await Role.filter(id=role_id, deleted_at__isnull=True).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    user_roles = await RBACService.get_role_users(role_id)

    total = len(user_roles)
    offset = (page - 1) * per_page
    paginated_roles = user_roles[offset : offset + per_page]

    total_pages = (total + per_page - 1) // per_page

    return UserRoleListResponse(
        user_roles=[UserRoleResponse.model_validate(ur) for ur in paginated_roles],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Current User RBAC Endpoints
@router.get("/me/roles", response_model=List[RoleResponse])
async def get_my_roles(current_user: User = Depends(get_current_active_user)):
    """Get current user's roles."""
    roles = await RBACService.get_user_roles(current_user.id)
    return [RoleResponse.model_validate(role) for role in roles]


@router.get("/me/permissions", response_model=List[str])
async def get_my_permissions(current_user: User = Depends(get_current_active_user)):
    """Get current user's permissions."""
    permissions = await RBACService.get_user_permissions(current_user.id)
    return list(permissions)


@router.post("/me/permissions/check", response_model=PermissionCheckResponse)
async def check_my_permissions(
    check_data: PermissionCheckRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Check if current user has specific permissions."""
    user_permissions = await RBACService.get_user_permissions(current_user.id)

    if check_data.require_all:
        has_permission = all(
            perm in user_permissions for perm in check_data.permissions
        )
        missing_permissions = [
            perm for perm in check_data.permissions if perm not in user_permissions
        ]
    else:
        has_permission = any(
            perm in user_permissions for perm in check_data.permissions
        )
        missing_permissions = [
            perm for perm in check_data.permissions if perm not in user_permissions
        ]

    return PermissionCheckResponse(
        has_permission=has_permission,
        missing_permissions=missing_permissions,
        user_permissions=list(user_permissions),
    )


# System Management Endpoints
@router.post("/initialize")
async def initialize_rbac_system(current_user: User = Depends(require_system_admin())):
    """Initialize the RBAC system with default roles."""
    await RBACService.initialize_default_roles()
    return {"message": "RBAC system initialized successfully"}


@router.get("/permissions", response_model=List[str])
async def list_all_permissions(_: User = Depends(require_user_manage())):
    """List all available permissions in the system."""
    return [permission.value for permission in PermissionType]
