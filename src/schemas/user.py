from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """User status enumeration for API."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


# Request Schemas
class UserRegisterRequest(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username (letters, numbers, underscores only)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserUpdateRequest(BaseModel):
    """Schema for user profile updates."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    phone: Optional[str] = Field(None, max_length=20)
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


class UserPasswordChangeRequest(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class UserPasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address for password reset")


class UserPasswordResetConfirmRequest(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")


# Response Schemas
class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: UserStatus
    is_verified: bool
    is_premium: bool
    total_trades: int
    successful_trades: int
    rating: float
    rating_count: int
    created_at: datetime
    last_active_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schema for user profile response (public view)."""
    id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    total_trades: int
    successful_trades: int
    rating: float
    rating_count: int
    created_at: datetime
    last_active_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """Schema for user statistics response."""
    total_trades: int
    successful_trades: int
    success_rate: float
    rating: float
    rating_count: int
    total_items: int
    active_items: int
    completed_trades_this_month: int
    completed_trades_this_year: int


class UserAuthResponse(BaseModel):
    """Schema for authentication response."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserListResponse(BaseModel):
    """Schema for user list response."""
    users: List[UserProfileResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserSearchRequest(BaseModel):
    """Schema for user search request."""
    query: Optional[str] = Field(None, description="Search query for username or name")
    city: Optional[str] = Field(None, description="Filter by city")
    state: Optional[str] = Field(None, description="Filter by state")
    country: Optional[str] = Field(None, description="Filter by country")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    min_trades: Optional[int] = Field(None, ge=0, description="Minimum number of trades")
    is_verified: Optional[bool] = Field(None, description="Filter by verification status")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""
    notification_email: bool
    notification_push: bool
    notification_sms: bool
    language: str
    timezone: str


class UserPreferencesUpdateRequest(BaseModel):
    """Schema for user preferences update."""
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_sms: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50) 