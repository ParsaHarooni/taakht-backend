from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from src.models.user import User
from src.services.auth import AuthService
from src.services.user import UserService
from src.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserUpdateRequest,
    UserResponse, UserProfileResponse, UserAuthResponse, UserStatsResponse,
    UserListResponse, UserSearchRequest, UserPasswordChangeRequest,
    UserPasswordResetRequest, UserPasswordResetConfirmRequest,
    UserPreferencesResponse, UserPreferencesUpdateRequest
)
from src.middlewares.auth import get_current_active_user, get_current_verified_user, get_optional_user
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """Register a new user account."""
    user = await AuthService.register_user(user_data)
    
    # Create tokens for immediate login
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)
    
    return UserAuthResponse(
        user=UserResponse.from_orm(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=UserAuthResponse)
async def login_user(login_data: UserLoginRequest):
    """Login user and return authentication tokens."""
    user, access_token, refresh_token = await AuthService.login_user(login_data)
    
    return UserAuthResponse(
        user=UserResponse.from_orm(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    access_token = await AuthService.refresh_access_token(refresh_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile."""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile."""
    updated_user = await UserService.update_user_profile(current_user, update_data)
    return UserResponse.from_orm(updated_user)


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_current_user_stats(current_user: User = Depends(get_current_active_user)):
    """Get current user's statistics."""
    return await UserService.get_user_stats(current_user.id)


@router.get("/me/items")
async def get_current_user_items(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's items."""
    result = await UserService.get_user_items(current_user.id, page, per_page)
    return {
        "items": result["items"],
        "pagination": {
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"]
        }
    }


@router.get("/me/trades")
async def get_current_user_trades(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's trades."""
    result = await UserService.get_user_trades(current_user.id, page, per_page)
    return {
        "trades": result["trades"],
        "pagination": {
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"]
        }
    }


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_current_user_preferences(current_user: User = Depends(get_current_active_user)):
    """Get current user's preferences."""
    return UserPreferencesResponse(
        notification_email=current_user.notification_email,
        notification_push=current_user.notification_push,
        notification_sms=current_user.notification_sms,
        language=current_user.language,
        timezone=current_user.timezone
    )


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_current_user_preferences(
    preferences: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's preferences."""
    update_data = UserUpdateRequest(**preferences.dict(exclude_unset=True))
    updated_user = await UserService.update_user_profile(current_user, update_data)
    
    return UserPreferencesResponse(
        notification_email=updated_user.notification_email,
        notification_push=updated_user.notification_push,
        notification_sms=updated_user.notification_sms,
        language=updated_user.language,
        timezone=updated_user.timezone
    )


@router.post("/me/change-password")
async def change_password(
    password_data: UserPasswordChangeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Change current user's password."""
    await AuthService.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password changed successfully"}


@router.post("/password-reset")
async def request_password_reset(reset_data: UserPasswordResetRequest):
    """Request password reset."""
    await AuthService.request_password_reset(reset_data.email)
    return {"message": "Password reset email sent (if email exists)"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(reset_data: UserPasswordResetConfirmRequest):
    """Confirm password reset with token."""
    await AuthService.reset_password_with_token(reset_data.token, reset_data.new_password)
    return {"message": "Password reset successfully"}


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get public user profile."""
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfileResponse.from_orm(user)


@router.get("/{user_id}/items")
async def get_user_items(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get user's public items."""
    user = await UserService.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = await UserService.get_user_items(user_id, page, per_page)
    return {
        "items": result["items"],
        "pagination": {
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"]
        }
    }


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: int):
    """Get user's public statistics."""
    user = await UserService.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return await UserService.get_user_stats(user_id)


@router.get("/", response_model=UserListResponse)
async def search_users(
    query: Optional[str] = Query(None, description="Search query"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    min_trades: Optional[int] = Query(None, ge=0, description="Minimum trades"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search and filter users."""
    search_request = UserSearchRequest(
        query=query,
        city=city,
        state=state,
        country=country,
        min_rating=min_rating,
        min_trades=min_trades,
        is_verified=is_verified,
        page=page,
        per_page=per_page
    )
    
    result = await UserService.search_users(search_request)
    
    return UserListResponse(
        users=[UserProfileResponse.from_orm(user) for user in result["users"]],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"]
    )


@router.delete("/me")
async def deactivate_account(current_user: User = Depends(get_current_active_user)):
    """Deactivate current user's account."""
    await UserService.deactivate_user(current_user)
    return {"message": "Account deactivated successfully"}


@router.delete("/me/permanent")
async def delete_account(current_user: User = Depends(get_current_active_user)):
    """Permanently delete current user's account."""
    await UserService.delete_user(current_user)
    return {"message": "Account deleted successfully"} 