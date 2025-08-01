import enum
import re

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinLengthValidator


class UserStatus(str, enum.Enum):
    """User status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(models.Model):
    """User model for authentication and user management."""

    id = fields.IntField(pk=True)

    # Authentication fields
    username = fields.CharField(
        max_length=50, unique=True, index=True, validators=[MinLengthValidator(3)]
    )
    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)

    # Profile fields
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)
    bio = fields.TextField(null=True)
    avatar_url = fields.CharField(max_length=500, null=True)
    phone = fields.CharField(max_length=20, null=True)

    # Location fields
    city = fields.CharField(max_length=100, null=True)
    state = fields.CharField(max_length=100, null=True)
    country = fields.CharField(max_length=100, null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)

    # Status and verification
    status = fields.CharEnumField(UserStatus, default=UserStatus.ACTIVE, index=True)
    is_verified = fields.BooleanField(default=False, index=True)
    is_premium = fields.BooleanField(default=False, index=True)
    email_verified_at = fields.DatetimeField(null=True)
    phone_verified_at = fields.DatetimeField(null=True)

    # Preferences
    notification_email = fields.BooleanField(default=True)
    notification_push = fields.BooleanField(default=True)
    notification_sms = fields.BooleanField(default=False)
    language = fields.CharField(max_length=10, default="en")
    timezone = fields.CharField(max_length=50, default="UTC")

    # Statistics
    total_trades = fields.IntField(default=0)
    successful_trades = fields.IntField(default=0)
    rating = fields.FloatField(default=0.0)
    rating_count = fields.IntField(default=0)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login_at = fields.DatetimeField(null=True)
    last_active_at = fields.DatetimeField(null=True)

    # Soft delete
    deleted_at = fields.DatetimeField(null=True, index=True)

    class Meta:
        table = "users"
        indexes = [
            ("username", "email"),
            ("status", "is_verified"),
            ("created_at", "status"),
        ]

    def __str__(self):
        return f"User(id={self.id}, username='{self.username}')"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE and not self.deleted_at

    @property
    def success_rate(self) -> float:
        """Calculate trade success rate."""
        if self.total_trades == 0:
            return 0.0
        return (self.successful_trades / self.total_trades) * 100

    async def save(self, *args, **kwargs):
        """Override save to add validation."""
        # Validate username format
        if not re.match(r"^[a-zA-Z0-9_]+$", self.username):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )

        # Validate email format
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.email):
            raise ValueError("Invalid email format")

        await super().save(*args, **kwargs)


# Pydantic models for API
User_Pydantic = pydantic_model_creator(
    User, name="User", exclude=("password_hash", "deleted_at")
)
UserIn_Pydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
    exclude=(
        "password_hash",
        "deleted_at",
        "status",
        "is_verified",
        "rating",
        "rating_count",
    ),
)
UserUpdate_Pydantic = pydantic_model_creator(
    User,
    name="UserUpdate",
    exclude_readonly=True,
    exclude=(
        "password_hash",
        "deleted_at",
        "status",
        "is_verified",
        "rating",
        "rating_count",
        "total_trades",
        "successful_trades",
    ),
)
