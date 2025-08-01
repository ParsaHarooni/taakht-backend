"""RBAC (Role-Based Access Control) schemas for Taakht backend.

This module provides Pydantic schemas for RBAC-related API requests and responses,
including role management, user role assignments, and permission checking.
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.models.role import PermissionType


class RoleResponse(BaseModel):
    """Schema for role response."""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    is_system_role: bool
    is_default: bool
    priority: int
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleCreateRequest(BaseModel):
    """Schema for role creation request."""

    name: str = Field(..., min_length=2, max_length=100, description="Role name")
    slug: str = Field(..., min_length=2, max_length=100, description="Role slug")
    description: Optional[str] = Field(None, description="Role description")
    priority: int = Field(0, ge=0, description="Role priority")
    permissions: List[str] = Field(default_factory=list, description="Role permissions")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug can only contain lowercase letters, numbers, and hyphens"
            )
        return v

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v):
        valid_permissions = [perm.value for perm in PermissionType]
        for perm in v:
            if perm not in valid_permissions:
                raise ValueError(f"Invalid permission: {perm}")
        return v


class RoleUpdateRequest(BaseModel):
    """Schema for role update request."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    permissions: Optional[List[str]] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug can only contain lowercase letters, numbers, and hyphens"
            )
        return v

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v):
        if v is not None:
            valid_permissions = [perm.value for perm in PermissionType]
            for perm in v:
                if perm not in valid_permissions:
                    raise ValueError(f"Invalid permission: {perm}")
        return v


class UserRoleResponse(BaseModel):
    """Schema for user role assignment response."""

    id: int
    user_id: int
    role_id: int
    assigned_by_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    role: RoleResponse

    model_config = {"from_attributes": True}


class UserRoleAssignRequest(BaseModel):
    """Schema for user role assignment request."""

    role_id: int = Field(..., description="Role ID to assign")
    reason: Optional[str] = Field(None, description="Reason for assignment")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")


class UserPermissionsResponse(BaseModel):
    """Schema for user permissions response."""

    user_id: int
    permissions: List[str]
    roles: List[str]


class PermissionCheckRequest(BaseModel):
    """Schema for permission check request."""

    permissions: List[str] = Field(..., description="Permissions to check")
    require_all: bool = Field(False, description="Require all permissions")

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v):
        valid_permissions = [perm.value for perm in PermissionType]
        for perm in v:
            if perm not in valid_permissions:
                raise ValueError(f"Invalid permission: {perm}")
        return v


class PermissionCheckResponse(BaseModel):
    """Schema for permission check response."""

    has_permission: bool
    missing_permissions: List[str]
    user_permissions: List[str]


class RoleListResponse(BaseModel):
    """Schema for role list response."""

    roles: List[RoleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserRoleListResponse(BaseModel):
    """Schema for user role list response."""

    user_roles: List[UserRoleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
