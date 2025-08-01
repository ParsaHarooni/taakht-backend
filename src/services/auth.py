import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import settings
from src.models.user import User, UserStatus
from src.schemas.user import UserLoginRequest, UserRegisterRequest

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for user management."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def register_user(user_data: UserRegisterRequest) -> User:
        """Register a new user."""
        # Check if username already exists
        existing_user = await User.filter(username=user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check if email already exists
        existing_email = await User.filter(email=user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = AuthService.get_password_hash(user_data.password)
        user = await User.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            status=UserStatus.ACTIVE,
        )

        # Assign default roles to new user
        from src.services.rbac import RBACService

        await RBACService.assign_default_roles_to_user(user.id)

        logger.info(f"New user registered: {user.username}")
        return user

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        # Try to find user by username or email
        user = await User.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    async def login_user(login_data: UserLoginRequest) -> Tuple[User, str, str]:
        """Login user and return user with tokens."""
        user = await AuthService.authenticate_user(
            login_data.username, login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login and active time
        user.last_login_at = datetime.now(timezone.utc)
        user.last_active_at = datetime.now(timezone.utc)
        await user.save(update_fields=["last_login_at", "last_active_at"])

        # Create tokens
        token_data = {"sub": str(user.id), "username": user.username}
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)

        logger.info(f"User logged in: {user.username}")
        return user, access_token, refresh_token

    @staticmethod
    async def get_current_user(token: str) -> User:
        """Get current user from JWT token."""
        payload = AuthService.verify_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await User.filter(id=int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last active time
        user.last_active_at = datetime.now(timezone.utc)
        await user.save(update_fields=["last_active_at"])

        return user

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> str:
        """Refresh access token using refresh token."""
        payload = AuthService.verify_token(refresh_token)
        token_type: str = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: str = payload.get("sub")
        username: str = payload.get("username")

        # Create new access token
        token_data = {"sub": user_id, "username": username}
        access_token = AuthService.create_access_token(token_data)

        return access_token

    @staticmethod
    async def change_password(
        user: User, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        if not AuthService.verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.password_hash = AuthService.get_password_hash(new_password)
        await user.save(update_fields=["password_hash"])

        logger.info(f"Password changed for user: {user.username}")
        return True

    @staticmethod
    async def request_password_reset(email: str) -> bool:
        """Request password reset (placeholder for email functionality)."""
        user = await User.filter(email=email).first()
        if not user:
            # Don't reveal if email exists or not
            return True

        # TODO: Implement email sending with reset token
        # For now, just log the request
        logger.info(f"Password reset requested for email: {email}")
        return True

    @staticmethod
    async def reset_password_with_token(token: str, new_password: str) -> bool:
        """Reset password using token (placeholder)."""
        # TODO: Implement token verification and password reset
        # For now, just log the request

        logger.info(f"Password reset with token: {token[:10]}...")
        return True
