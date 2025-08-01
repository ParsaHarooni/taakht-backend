"""User management schemas for Taakht backend.

This module provides Pydantic schemas for user-related API requests and responses,
including authentication, profile management, and user administration.
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.models.user import UserStatus


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserAuthResponse(BaseModel):
    """Schema for user authentication response."""

    user: "UserResponse"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    is_active: bool
    status: UserStatus
    rating: float
    total_trades: int
    successful_trades: int
    failed_trades: int
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notification_email: bool
    notification_push: bool
    notification_sms: bool
    language: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""

    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    is_active: bool
    status: UserStatus
    rating: float
    total_trades: int
    successful_trades: int
    failed_trades: int
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notification_email: bool
    notification_push: bool
    notification_sms: bool
    language: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Schema for user profile update request."""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_sms: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""

    notification_email: bool
    notification_push: bool
    notification_sms: bool
    language: str
    timezone: str

    model_config = {"from_attributes": True}


class UserPreferencesUpdateRequest(BaseModel):
    """Schema for user preferences update request."""

    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_sms: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)


class UserPasswordChangeRequest(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class UserPasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: str = Field(..., description="Email address")


class UserPasswordResetConfirmRequest(BaseModel):
    """Schema for password reset confirmation request."""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class UserStatsResponse(BaseModel):
    """Schema for user statistics response."""

    total_items: int
    available_items: int
    reserved_items: int
    traded_items: int
    total_views: int
    total_favorites: int
    total_trade_offers: int
    average_rating: float
    total_reviews: int
    positive_reviews: int
    negative_reviews: int

    model_config = {"from_attributes": True}


class UserSearchRequest(BaseModel):
    """Schema for user search request."""

    query: Optional[str] = Field(None, description="Search query")
    city: Optional[str] = Field(None, description="Filter by city")
    state: Optional[str] = Field(None, description="Filter by state")
    country: Optional[str] = Field(None, description="Filter by country")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    min_trades: Optional[int] = Field(None, ge=0, description="Minimum trades")
    is_verified: Optional[bool] = Field(None, description="Filter by verification")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class UserListResponse(BaseModel):
    """Schema for user list response."""

    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
