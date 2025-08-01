import logging
from datetime import datetime, timezone
from typing import List, Optional, Set

from fastapi import HTTPException, status

from src.models.role import PermissionType, Role, UserRole
from src.models.user import User
from src.schemas.rbac import RoleCreateRequest, RoleUpdateRequest

logger = logging.getLogger(__name__)


class RBACService:
    """Role-Based Access Control service for managing roles and permissions."""

    # Default roles and permissions
    DEFAULT_ROLES = {
        "user": {
            "name": "User",
            "slug": "user",
            "description": "Regular user with basic permissions",
            "is_default": True,
            "priority": 0,
            "permissions": [
                PermissionType.USER_READ,
                PermissionType.USER_UPDATE,
                PermissionType.ITEM_READ,
                PermissionType.ITEM_CREATE,
                PermissionType.ITEM_UPDATE,
                PermissionType.ITEM_DELETE,
                PermissionType.TRADE_READ,
                PermissionType.TRADE_CREATE,
                PermissionType.TRADE_UPDATE,
                PermissionType.CATEGORY_READ,
            ],
        },
        "moderator": {
            "name": "Moderator",
            "slug": "moderator",
            "description": "Content moderator with moderation permissions",
            "is_default": False,
            "priority": 50,
            "permissions": [
                PermissionType.USER_READ,
                PermissionType.USER_UPDATE,
                PermissionType.ITEM_READ,
                PermissionType.ITEM_UPDATE,
                PermissionType.ITEM_DELETE,
                PermissionType.TRADE_READ,
                PermissionType.TRADE_UPDATE,
                PermissionType.CATEGORY_READ,
                PermissionType.CATEGORY_UPDATE,
                PermissionType.MODERATE_USERS,
                PermissionType.MODERATE_ITEMS,
                PermissionType.MODERATE_TRADES,
                PermissionType.MODERATE_CONTENT,
            ],
        },
        "admin": {
            "name": "Administrator",
            "slug": "admin",
            "description": "System administrator with full permissions",
            "is_default": False,
            "priority": 100,
            "permissions": [
                PermissionType.USER_READ,
                PermissionType.USER_CREATE,
                PermissionType.USER_UPDATE,
                PermissionType.USER_DELETE,
                PermissionType.USER_MANAGE,
                PermissionType.ITEM_READ,
                PermissionType.ITEM_CREATE,
                PermissionType.ITEM_UPDATE,
                PermissionType.ITEM_DELETE,
                PermissionType.ITEM_MANAGE,
                PermissionType.TRADE_READ,
                PermissionType.TRADE_CREATE,
                PermissionType.TRADE_UPDATE,
                PermissionType.TRADE_DELETE,
                PermissionType.TRADE_MANAGE,
                PermissionType.CATEGORY_READ,
                PermissionType.CATEGORY_CREATE,
                PermissionType.CATEGORY_UPDATE,
                PermissionType.CATEGORY_DELETE,
                PermissionType.CATEGORY_MANAGE,
                PermissionType.SYSTEM_READ,
                PermissionType.SYSTEM_MANAGE,
                PermissionType.SYSTEM_ADMIN,
                PermissionType.MODERATE_USERS,
                PermissionType.MODERATE_ITEMS,
                PermissionType.MODERATE_TRADES,
                PermissionType.MODERATE_CONTENT,
            ],
        },
    }

    @staticmethod
    async def initialize_default_roles():
        """Initialize default roles in the system."""
        for role_data in RBACService.DEFAULT_ROLES.values():
            role, created = await Role.get_or_create(
                slug=role_data["slug"],
                defaults={
                    "name": role_data["name"],
                    "description": role_data["description"],
                    "is_system_role": True,
                    "is_default": role_data["is_default"],
                    "priority": role_data["priority"],
                    "permissions": role_data["permissions"],
                },
            )

            if created:
                logger.info(f"Created default role: {role.name}")
            else:
                # Update existing role permissions if needed
                if role.permissions != role_data["permissions"]:
                    role.permissions = role_data["permissions"]
                    await role.save(update_fields=["permissions"])
                    logger.info(f"Updated role permissions: {role.name}")

    @staticmethod
    async def get_user_roles(user_id: int) -> List[Role]:
        """Get all active roles for a user."""
        user_roles = await UserRole.filter(
            user_id=user_id, role__deleted_at__isnull=True
        ).prefetch_related("role")

        active_roles = []
        for user_role in user_roles:
            if user_role.is_active:
                active_roles.append(user_role.role)

        return active_roles

    @staticmethod
    async def get_user_permissions(user_id: int) -> Set[str]:
        """Get all permissions for a user from their roles."""
        roles = await RBACService.get_user_roles(user_id)
        permissions = set()

        for role in roles:
            permissions.update(role.permissions)

        return permissions

    @staticmethod
    async def has_permission(user_id: int, permission: str) -> bool:
        """Check if user has a specific permission."""
        permissions = await RBACService.get_user_permissions(user_id)
        return permission in permissions

    @staticmethod
    async def has_any_permission(user_id: int, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        user_permissions = await RBACService.get_user_permissions(user_id)
        return any(permission in user_permissions for permission in permissions)

    @staticmethod
    async def has_all_permissions(user_id: int, permissions: List[str]) -> bool:
        """Check if user has all of the specified permissions."""
        user_permissions = await RBACService.get_user_permissions(user_id)
        return all(permission in user_permissions for permission in permissions)

    @staticmethod
    async def assign_role_to_user(
        user_id: int,
        role_id: int,
        assigned_by_id: int,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserRole:
        """Assign a role to a user."""
        # Check if role exists and is active
        role = await Role.filter(id=role_id, deleted_at__isnull=True).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        # Check if user exists
        user = await User.filter(id=user_id, deleted_at__isnull=True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check if assignment already exists
        existing_assignment = await UserRole.filter(
            user_id=user_id, role_id=role_id
        ).first()
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this role",
            )

        # Create role assignment
        user_role = await UserRole.create(
            user_id=user_id,
            role_id=role_id,
            assigned_by_id=assigned_by_id,
            reason=reason,
            expires_at=expires_at,
        )

        logger.info(
            f"Role '{role.name}' assigned to user {user_id} by {assigned_by_id}"
        )
        return user_role

    @staticmethod
    async def remove_role_from_user(
        user_id: int, role_id: int, removed_by_id: int
    ) -> bool:
        """Remove a role from a user."""
        user_role = await UserRole.filter(user_id=user_id, role_id=role_id).first()
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found",
            )

        await user_role.delete()
        logger.info(f"Role {role_id} removed from user {user_id} by {removed_by_id}")
        return True

    @staticmethod
    async def create_role(role_data: RoleCreateRequest, created_by_id: int) -> Role:
        """Create a new role."""
        # Check if role with same slug already exists
        existing_role = await Role.filter(
            slug=role_data.slug, deleted_at__isnull=True
        ).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this slug already exists",
            )

        role = await Role.create(
            name=role_data.name,
            slug=role_data.slug,
            description=role_data.description,
            priority=role_data.priority,
            permissions=role_data.permissions,
            is_default=role_data.is_default,
        )

        logger.info(f"Role '{role.name}' created by user {created_by_id}")
        return role

    @staticmethod
    async def update_role(
        role_id: int, role_data: RoleUpdateRequest, updated_by_id: int
    ) -> Role:
        """Update an existing role."""
        role = await Role.filter(id=role_id, deleted_at__isnull=True).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify system roles",
            )

        # Update role fields
        update_fields = []
        if role_data.name is not None:
            role.name = role_data.name
            update_fields.append("name")

        if role_data.description is not None:
            role.description = role_data.description
            update_fields.append("description")

        if role_data.priority is not None:
            role.priority = role_data.priority
            update_fields.append("priority")

        if role_data.permissions is not None:
            role.permissions = role_data.permissions
            update_fields.append("permissions")

        if role_data.is_default is not None:
            role.is_default = role_data.is_default
            update_fields.append("is_default")

        if update_fields:
            await role.save(update_fields=update_fields)
            logger.info(f"Role '{role.name}' updated by user {updated_by_id}")

        return role

    @staticmethod
    async def delete_role(role_id: int, deleted_by_id: int) -> bool:
        """Soft delete a role."""
        role = await Role.filter(id=role_id, deleted_at__isnull=True).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system roles",
            )

        # Check if role is assigned to any users
        user_count = await UserRole.filter(role_id=role_id).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role: {user_count} users have this role assigned",
            )

        role.deleted_at = datetime.now(timezone.utc)
        await role.save(update_fields=["deleted_at"])

        logger.info(f"Role '{role.name}' deleted by user {deleted_by_id}")
        return True

    @staticmethod
    async def get_user_role_assignments(user_id: int) -> List[UserRole]:
        """Get all role assignments for a user."""
        return await UserRole.filter(user_id=user_id).prefetch_related(
            "role", "assigned_by"
        )

    @staticmethod
    async def get_role_users(role_id: int) -> List[UserRole]:
        """Get all users assigned to a role."""
        return await UserRole.filter(role_id=role_id).prefetch_related(
            "user", "assigned_by"
        )

    @staticmethod
    async def assign_default_roles_to_user(user_id: int) -> List[UserRole]:
        """Assign default roles to a new user."""
        default_roles = await Role.filter(is_default=True, deleted_at__isnull=True)
        user_roles = []

        for role in default_roles:
            user_role = await UserRole.create(
                user_id=user_id,
                role_id=role.id,
                assigned_by_id=None,  # System assignment
                reason="Default role assignment",
            )
            user_roles.append(user_role)

        logger.info(f"Default roles assigned to new user {user_id}")
        return user_roles
