from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from src.models.user import User, UserStatus
from src.models.item import Item, ItemStatus
from src.models.trade import Trade, TradeStatus
from src.schemas.user import UserUpdateRequest, UserSearchRequest, UserStatsResponse
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User service for profile management and user operations."""
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await User.filter(id=user_id, deleted_at__isnull=True).first()
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        return await User.filter(username=username, deleted_at__isnull=True).first()
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        return await User.filter(email=email, deleted_at__isnull=True).first()
    
    @staticmethod
    async def update_user_profile(user: User, update_data: UserUpdateRequest) -> User:
        """Update user profile."""
        update_fields = []
        
        # Update basic profile fields
        if update_data.first_name is not None:
            user.first_name = update_data.first_name
            update_fields.append("first_name")
        
        if update_data.last_name is not None:
            user.last_name = update_data.last_name
            update_fields.append("last_name")
        
        if update_data.bio is not None:
            user.bio = update_data.bio
            update_fields.append("bio")
        
        if update_data.phone is not None:
            user.phone = update_data.phone
            update_fields.append("phone")
        
        # Update location fields
        if update_data.city is not None:
            user.city = update_data.city
            update_fields.append("city")
        
        if update_data.state is not None:
            user.state = update_data.state
            update_fields.append("state")
        
        if update_data.country is not None:
            user.country = update_data.country
            update_fields.append("country")
        
        if update_data.latitude is not None:
            user.latitude = update_data.latitude
            update_fields.append("latitude")
        
        if update_data.longitude is not None:
            user.longitude = update_data.longitude
            update_fields.append("longitude")
        
        # Update notification preferences
        if update_data.notification_email is not None:
            user.notification_email = update_data.notification_email
            update_fields.append("notification_email")
        
        if update_data.notification_push is not None:
            user.notification_push = update_data.notification_push
            update_fields.append("notification_push")
        
        if update_data.notification_sms is not None:
            user.notification_sms = update_data.notification_sms
            update_fields.append("notification_sms")
        
        if update_data.language is not None:
            user.language = update_data.language
            update_fields.append("language")
        
        if update_data.timezone is not None:
            user.timezone = update_data.timezone
            update_fields.append("timezone")
        
        if update_fields:
            await user.save(update_fields=update_fields)
            logger.info(f"User profile updated: {user.username}")
        
        return user
    
    @staticmethod
    async def get_user_stats(user_id: int) -> UserStatsResponse:
        """Get comprehensive user statistics."""
        user = await User.get(id=user_id)
        
        # Get item statistics
        total_items = await Item.filter(owner_id=user_id, deleted_at__isnull=True).count()
        active_items = await Item.filter(
            owner_id=user_id, 
            status=ItemStatus.AVAILABLE,
            deleted_at__isnull=True
        ).count()
        
        # Get trade statistics
        total_trades = user.total_trades
        successful_trades = user.successful_trades
        success_rate = user.success_rate
        
        # Get monthly and yearly trade statistics
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        completed_trades_this_month = await Trade.filter(
            (Trade.initiator_id == user_id) | (Trade.recipient_id == user_id),
            status=TradeStatus.COMPLETED,
            completed_at__gte=month_start
        ).count()
        
        completed_trades_this_year = await Trade.filter(
            (Trade.initiator_id == user_id) | (Trade.recipient_id == user_id),
            status=TradeStatus.COMPLETED,
            completed_at__gte=year_start
        ).count()
        
        return UserStatsResponse(
            total_trades=total_trades,
            successful_trades=successful_trades,
            success_rate=success_rate,
            rating=user.rating,
            rating_count=user.rating_count,
            total_items=total_items,
            active_items=active_items,
            completed_trades_this_month=completed_trades_this_month,
            completed_trades_this_year=completed_trades_this_year
        )
    
    @staticmethod
    async def search_users(search_request: UserSearchRequest) -> Dict[str, Any]:
        """Search users with filters and pagination."""
        query = User.filter(deleted_at__isnull=True, status=UserStatus.ACTIVE)
        
        # Apply search filters
        if search_request.query:
            query = query.filter(
                (User.username.contains(search_request.query)) |
                (User.first_name.contains(search_request.query)) |
                (User.last_name.contains(search_request.query))
            )
        
        if search_request.city:
            query = query.filter(city__icontains=search_request.city)
        
        if search_request.state:
            query = query.filter(state__icontains=search_request.state)
        
        if search_request.country:
            query = query.filter(country__icontains=search_request.country)
        
        if search_request.min_rating is not None:
            query = query.filter(rating__gte=search_request.min_rating)
        
        if search_request.min_trades is not None:
            query = query.filter(total_trades__gte=search_request.min_trades)
        
        if search_request.is_verified is not None:
            query = query.filter(is_verified=search_request.is_verified)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.per_page
        users = await query.offset(offset).limit(search_request.per_page).order_by("-created_at")
        
        # Calculate pagination info
        total_pages = (total + search_request.per_page - 1) // search_request.per_page
        
        return {
            "users": users,
            "total": total,
            "page": search_request.page,
            "per_page": search_request.per_page,
            "total_pages": total_pages
        }
    
    @staticmethod
    async def get_user_items(user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get user's items with pagination."""
        query = Item.filter(owner_id=user_id, deleted_at__isnull=True)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        items = await query.offset(offset).limit(per_page).order_by("-created_at")
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    @staticmethod
    async def get_user_trades(user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get user's trades with pagination."""
        query = Trade.filter(
            (Trade.initiator_id == user_id) | (Trade.recipient_id == user_id),
            deleted_at__isnull=True
        )
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        trades = await query.offset(offset).limit(per_page).order_by("-created_at")
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "trades": trades,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    @staticmethod
    async def deactivate_user(user: User) -> bool:
        """Deactivate user account."""
        user.status = UserStatus.INACTIVE
        await user.save(update_fields=["status"])
        
        logger.info(f"User deactivated: {user.username}")
        return True
    
    @staticmethod
    async def delete_user(user: User) -> bool:
        """Soft delete user account."""
        user.deleted_at = datetime.now(timezone.utc)
        await user.save(update_fields=["deleted_at"])
        
        logger.info(f"User deleted: {user.username}")
        return True
    
    @staticmethod
    async def verify_user_email(user: User) -> bool:
        """Verify user email."""
        user.is_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        await user.save(update_fields=["is_verified", "email_verified_at"])
        
        logger.info(f"User email verified: {user.username}")
        return True
    
    @staticmethod
    async def update_user_rating(user: User, new_rating: float) -> bool:
        """Update user rating."""
        # Calculate new average rating
        total_rating = user.rating * user.rating_count + new_rating
        user.rating_count += 1
        user.rating = total_rating / user.rating_count
        
        await user.save(update_fields=["rating", "rating_count"])
        
        logger.info(f"User rating updated: {user.username} - {user.rating}")
        return True 