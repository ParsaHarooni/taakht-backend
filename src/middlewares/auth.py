from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.auth import AuthService
from src.models.user import User
from typing import Optional

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    user = await AuthService.get_current_user(token)
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    return current_user


async def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to get current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Dependency to get optional authenticated user (for public endpoints)."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await AuthService.get_current_user(token)
        return user
    except HTTPException:
        return None 