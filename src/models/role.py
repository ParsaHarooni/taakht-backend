import enum

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinLengthValidator


class PermissionType(str, enum.Enum):
    """Permission types for role-based access control."""

    # User permissions
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Item permissions
    ITEM_READ = "item:read"
    ITEM_CREATE = "item:create"
    ITEM_UPDATE = "item:update"
    ITEM_DELETE = "item:delete"
    ITEM_MANAGE = "item:manage"

    # Trade permissions
    TRADE_READ = "trade:read"
    TRADE_CREATE = "trade:create"
    TRADE_UPDATE = "trade:update"
    TRADE_DELETE = "trade:delete"
    TRADE_MANAGE = "trade:manage"

    # Category permissions
    CATEGORY_READ = "category:read"
    CATEGORY_CREATE = "category:create"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"
    CATEGORY_MANAGE = "category:manage"

    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_MANAGE = "system:manage"
    SYSTEM_ADMIN = "system:admin"

    # Moderation permissions
    MODERATE_USERS = "moderate:users"
    MODERATE_ITEMS = "moderate:items"
    MODERATE_TRADES = "moderate:trades"
    MODERATE_CONTENT = "moderate:content"


class Role(models.Model):
    """Role model for role-based access control."""

    id = fields.IntField(pk=True)

    # Basic role information
    name = fields.CharField(
        max_length=100, unique=True, index=True, validators=[MinLengthValidator(2)]
    )
    slug = fields.CharField(max_length=100, unique=True, index=True)
    description = fields.TextField(null=True)

    # Role metadata
    is_system_role = fields.BooleanField(
        default=False, index=True
    )  # Cannot be deleted/modified
    is_default = fields.BooleanField(default=False, index=True)  # Assigned to new users
    priority = fields.IntField(
        default=0, index=True
    )  # Higher priority roles override lower ones

    # Permissions
    permissions = fields.JSONField(default=list)  # List of permission strings

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True, index=True)

    class Meta:
        table = "roles"
        indexes = [
            ("is_system_role", "priority"),
            ("is_default", "priority"),
            ("slug", "deleted_at"),
        ]
        ordering = ["-priority", "name"]

    def __str__(self):
        return f"Role(id={self.id}, name='{self.name}', slug='{self.slug}')"

    @property
    def is_active(self) -> bool:
        """Check if role is active."""
        return not self.deleted_at

    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: list) -> bool:
        """Check if role has any of the specified permissions."""
        return any(permission in self.permissions for permission in permissions)

    def has_all_permissions(self, permissions: list) -> bool:
        """Check if role has all of the specified permissions."""
        return all(permission in self.permissions for permission in permissions)


class UserRole(models.Model):
    """UserRole model for assigning roles to users."""

    id = fields.IntField(pk=True)

    # Relationships
    user = fields.ForeignKeyField(
        "models.User", related_name="user_roles", on_delete=fields.CASCADE, index=True
    )
    role = fields.ForeignKeyField(
        "models.Role", related_name="user_roles", on_delete=fields.CASCADE, index=True
    )

    # Assignment metadata
    assigned_by = fields.ForeignKeyField(
        "models.User",
        related_name="role_assignments",
        on_delete=fields.SET_NULL,
        null=True,
        index=True,
    )
    reason = fields.TextField(null=True)  # Reason for role assignment

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    expires_at = fields.DatetimeField(null=True, index=True)  # Role expiration

    class Meta:
        table = "user_roles"
        indexes = [
            ("user_id", "role_id"),
            ("expires_at", "created_at"),
        ]
        unique_together = [("user_id", "role_id")]

    def __str__(self):
        return f"UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})"

    @property
    def is_active(self) -> bool:
        """Check if role assignment is active."""
        if not self.role.is_active:
            return False
        if self.expires_at:
            from datetime import datetime, timezone

            return datetime.now(timezone.utc) < self.expires_at
        return True


# Pydantic models for API
Role_Pydantic = pydantic_model_creator(Role, name="Role", exclude=("deleted_at",))
RoleIn_Pydantic = pydantic_model_creator(
    Role, name="RoleIn", exclude_readonly=True, exclude=("deleted_at", "is_system_role")
)
RoleUpdate_Pydantic = pydantic_model_creator(
    Role,
    name="RoleUpdate",
    exclude_readonly=True,
    exclude=("deleted_at", "is_system_role"),
)

UserRole_Pydantic = pydantic_model_creator(UserRole, name="UserRole")
UserRoleIn_Pydantic = pydantic_model_creator(
    UserRole, name="UserRoleIn", exclude_readonly=True, exclude=("user_id",)
)
