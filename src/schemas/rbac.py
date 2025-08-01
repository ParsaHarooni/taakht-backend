from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.models.role import PermissionType


class RoleResponse(BaseModel):
    """Schema for role response."""

    id: int
    name: str
    slug: str
    description: Optional[str]
    is_system_role: bool
    is_default: bool
    priority: int
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    """Schema for creating a new role."""

    name: str = Field(..., min_length=2, max_length=100, description="Role name")
    slug: str = Field(
        ..., min_length=2, max_length=100, description="Role slug (unique identifier)"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Role description"
    )
    priority: int = Field(
        0, ge=0, le=1000, description="Role priority (higher = more important)"
    )
    permissions: List[str] = Field(
        default_factory=list, description="List of permission strings"
    )
    is_default: bool = Field(
        False, description="Whether this role should be assigned to new users"
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        import re

        if not re.match(r"^[a-z0-9_-]+$", v):
            raise ValueError(
                "Slug can only contain lowercase letters, numbers, hyphens, and underscores"
            )
        return v

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v):
        valid_permissions = [p.value for p in PermissionType]
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f"Invalid permission: {permission}")
        return v


class RoleUpdateRequest(BaseModel):
    """Schema for updating a role."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=0, le=1000)
    permissions: Optional[List[str]] = None
    is_default: Optional[bool] = None

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v):
        if v is None:
            return v
        valid_permissions = [p.value for p in PermissionType]
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f"Invalid permission: {permission}")
        return v


class UserRoleResponse(BaseModel):
    """Schema for user role assignment response."""

    id: int
    user_id: int
    role_id: int
    assigned_by_id: Optional[int]
    reason: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    role: RoleResponse

    class Config:
        from_attributes = True


class UserRoleAssignRequest(BaseModel):
    """Schema for assigning a role to a user."""

    role_id: int = Field(..., description="ID of the role to assign")
    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for role assignment"
    )
    expires_at: Optional[datetime] = Field(
        None, description="When the role assignment expires"
    )


class UserPermissionsResponse(BaseModel):
    """Schema for user permissions response."""

    user_id: int
    permissions: List[str]
    roles: List[str]  # Role names


class PermissionCheckRequest(BaseModel):
    """Schema for checking user permissions."""

    permissions: List[str] = Field(..., description="Permissions to check")
    require_all: bool = Field(
        False, description="Whether all permissions are required or just one"
    )


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
