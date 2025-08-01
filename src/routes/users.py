"""User management API routes for Taakht backend.

This module provides comprehensive API endpoints for user management including
authentication, profile management, and user administration.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.middlewares.auth import get_current_active_user, get_optional_user
from src.schemas.user import (
    UserAuthResponse,
    UserListResponse,
    UserPasswordChangeRequest,
    UserPasswordResetConfirmRequest,
    UserPasswordResetRequest,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
    UserProfileResponse,
    UserRegisterRequest,
    UserResponse,
    UserSearchRequest,
    UserStatsResponse,
    UserUpdateRequest,
)
from src.services.auth import AuthService
from src.services.user import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


# Authentication Endpoints
@router.post(
    "/register", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserRegisterRequest):
    """Register a new user."""
    user = await AuthService.register_user(user_data)
    tokens = await AuthService.login_user(user)

    return UserAuthResponse(
        user=UserResponse.model_validate(user),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/login", response_model=UserAuthResponse)
async def login_user(login_data):
    """Login user with email/username and password."""
    user = await AuthService.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    tokens = await AuthService.login_user(user)

    return UserAuthResponse(
        user=UserResponse.model_validate(user),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/refresh", response_model=UserAuthResponse)
async def refresh_token(refresh_token_data):
    """Refresh access token using refresh token."""
    new_tokens = await AuthService.refresh_access_token(
        refresh_token_data.refresh_token
    )

    return UserAuthResponse(
        user=UserResponse.model_validate(new_tokens["user"]),
        access_token=new_tokens["access_token"],
        refresh_token=new_tokens["refresh_token"],
        token_type="bearer",
    )


# Current User Endpoints
@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user=Depends(get_current_active_user)):
    """Get current user's profile."""
    return UserProfileResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    user_data: UserUpdateRequest,
    current_user=Depends(get_current_active_user),
):
    """Update current user's profile."""
    updated_user = await UserService.update_user_profile(current_user.id, user_data)
    return UserProfileResponse.model_validate(updated_user)


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_current_user_stats(current_user=Depends(get_current_active_user)):
    """Get current user's statistics."""
    stats = await UserService.get_user_stats(current_user.id)
    return UserStatsResponse.model_validate(stats)


@router.get("/me/items")
async def get_current_user_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_active_user),
):
    """Get current user's items."""
    items, total = await UserService.get_user_items(current_user.id, page, per_page)

    total_pages = (total + per_page - 1) // per_page

    return {
        "items": [UserResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/me/trades")
async def get_current_user_trades(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_active_user),
):
    """Get current user's trades."""
    trades, total = await UserService.get_user_trades(current_user.id, page, per_page)

    total_pages = (total + per_page - 1) // per_page

    return {
        "trades": trades,  # TODO: Create TradeResponse schema
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_current_user_preferences(current_user=Depends(get_current_active_user)):
    """Get current user's preferences."""
    return UserPreferencesResponse.model_validate(current_user)


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_current_user_preferences(
    preferences: UserPreferencesUpdateRequest,
    current_user=Depends(get_current_active_user),
):
    """Update current user's preferences."""
    updated_user = await UserService.update_user_profile(current_user.id, preferences)
    return UserPreferencesResponse.model_validate(updated_user)


@router.post("/me/change-password")
async def change_password(
    password_data: UserPasswordChangeRequest,
    current_user=Depends(get_current_active_user),
):
    """Change current user's password."""
    await AuthService.change_password(current_user.id, password_data)
    return {"message": "Password changed successfully"}


@router.delete("/me")
async def deactivate_account(current_user=Depends(get_current_active_user)):
    """Deactivate current user's account."""
    await UserService.deactivate_user(current_user.id)
    return {"message": "Account deactivated successfully"}


@router.delete("/me/permanent")
async def delete_account_permanently(current_user=Depends(get_current_active_user)):
    """Permanently delete current user's account."""
    await UserService.delete_user(current_user.id)
    return {"message": "Account deleted permanently"}


# Password Reset Endpoints
@router.post("/password-reset")
async def request_password_reset(reset_data: UserPasswordResetRequest):
    """Request password reset."""
    await AuthService.request_password_reset(reset_data.email)
    return {"message": "Password reset email sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(confirm_data: UserPasswordResetConfirmRequest):
    """Confirm password reset with token."""
    await AuthService.reset_password_with_token(
        confirm_data.token, confirm_data.new_password
    )
    return {"message": "Password reset successfully"}


# Public User Endpoints
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    _: Optional = Depends(get_optional_user),
):
    """Get public user profile."""
    user = await UserService.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.get("/{user_id}/items")
async def get_user_items(
    user_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: Optional = Depends(get_optional_user),
):
    """Get public user's items."""
    user = await UserService.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    items, total = await UserService.get_user_items(user_id, page, per_page)

    total_pages = (total + per_page - 1) // per_page

    return {
        "items": [UserResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int,
    _: Optional = Depends(get_optional_user),
):
    """Get public user's statistics."""
    user = await UserService.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    stats = await UserService.get_user_stats(user_id)
    return UserStatsResponse.model_validate(stats)


# User Search and List Endpoints
@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: Optional = Depends(get_optional_user),
):
    """List users with pagination."""
    users, total = await UserService.search_users(
        UserSearchRequest(page=page, per_page=per_page)
    )

    total_pages = (total + per_page - 1) // per_page

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/search", response_model=UserListResponse)
async def search_users(
    search_data: UserSearchRequest,
    _: Optional = Depends(get_optional_user),
):
    """Search users with filters."""
    users, total = await UserService.search_users(search_data)

    total_pages = (total + search_data.per_page - 1) // search_data.per_page

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=search_data.page,
        per_page=search_data.per_page,
        total_pages=total_pages,
    )
