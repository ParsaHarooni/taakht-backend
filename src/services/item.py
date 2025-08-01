import logging
import math
import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException, status

from src.models.category import Category
from src.models.item import Item, ItemStatus
from src.schemas.item import (
    ItemBulkUpdateRequest,
    ItemCreateRequest,
    ItemDuplicateRequest,
    ItemSearchRequest,
    ItemStatsResponse,
    ItemUpdateRequest,
)
from src.services.rbac import RBACService

logger = logging.getLogger(__name__)


class ItemService:
    """Service for item-related business logic."""

    @staticmethod
    async def create_item(item_data: ItemCreateRequest, owner_id: int) -> Item:
        """Create a new item."""
        # Check if category exists
        category = await Category.filter(
            id=item_data.category_id, deleted_at__isnull=True
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        # Generate slug from title
        slug = ItemService._generate_slug(item_data.title)

        # Create item
        item = await Item.create(
            title=item_data.title,
            description=item_data.description,
            condition=item_data.condition,
            owner_id=owner_id,
            category_id=item_data.category_id,
            estimated_value=item_data.estimated_value,
            currency=item_data.currency,
            weight_kg=item_data.weight_kg,
            length_cm=item_data.length_cm,
            width_cm=item_data.width_cm,
            height_cm=item_data.height_cm,
            city=item_data.city,
            state=item_data.state,
            country=item_data.country,
            latitude=item_data.latitude,
            longitude=item_data.longitude,
            tags=item_data.tags,
            attributes=item_data.attributes,
            trade_for=item_data.trade_for,
            trade_radius_km=item_data.trade_radius_km,
            shipping_available=item_data.shipping_available,
            local_pickup_only=item_data.local_pickup_only,
            meta_title=item_data.meta_title or item_data.title,
            meta_description=item_data.meta_description or item_data.description[:160],
            slug=slug,
        )

        logger.info(f"Item created: {item.title} by user {owner_id}")
        return item

    @staticmethod
    async def get_item_by_id(
        item_id: int, include_deleted: bool = False
    ) -> Optional[Item]:
        """Get item by ID."""
        query = Item.all()
        if not include_deleted:
            query = query.filter(deleted_at__isnull=True)

        return (
            await query.filter(id=item_id).prefetch_related("owner", "category").first()
        )

    @staticmethod
    async def get_item_by_slug(
        slug: str, include_deleted: bool = False
    ) -> Optional[Item]:
        """Get item by slug."""
        query = Item.all()
        if not include_deleted:
            query = query.filter(deleted_at__isnull=True)

        return (
            await query.filter(slug=slug).prefetch_related("owner", "category").first()
        )

    @staticmethod
    async def update_item(
        item_id: int, item_data: ItemUpdateRequest, user_id: int
    ) -> Item:
        """Update an item."""
        item = await ItemService.get_item_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

        # Check ownership or management permission
        if item.owner_id != user_id:
            has_manage_perm = await RBACService.has_permission(user_id, "item:manage")
            if not has_manage_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own items",
                )

        # Check if category exists if being updated
        if item_data.category_id is not None:
            category = await Category.filter(
                id=item_data.category_id, deleted_at__isnull=True
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

        # Update fields
        update_fields = []

        if item_data.title is not None:
            item.title = item_data.title
            item.slug = ItemService._generate_slug(item_data.title)
            update_fields.extend(["title", "slug"])

        if item_data.description is not None:
            item.description = item_data.description
            update_fields.append("description")

        if item_data.condition is not None:
            item.condition = item_data.condition
            update_fields.append("condition")

        if item_data.status is not None:
            item.status = item_data.status
            update_fields.append("status")

        if item_data.category_id is not None:
            item.category_id = item_data.category_id
            update_fields.append("category_id")

        if item_data.estimated_value is not None:
            item.estimated_value = item_data.estimated_value
            update_fields.append("estimated_value")

        if item_data.currency is not None:
            item.currency = item_data.currency
            update_fields.append("currency")

        if item_data.weight_kg is not None:
            item.weight_kg = item_data.weight_kg
            update_fields.append("weight_kg")

        if item_data.length_cm is not None:
            item.length_cm = item_data.length_cm
            update_fields.append("length_cm")

        if item_data.width_cm is not None:
            item.width_cm = item_data.width_cm
            update_fields.append("width_cm")

        if item_data.height_cm is not None:
            item.height_cm = item_data.height_cm
            update_fields.append("height_cm")

        if item_data.city is not None:
            item.city = item_data.city
            update_fields.append("city")

        if item_data.state is not None:
            item.state = item_data.state
            update_fields.append("state")

        if item_data.country is not None:
            item.country = item_data.country
            update_fields.append("country")

        if item_data.latitude is not None:
            item.latitude = item_data.latitude
            update_fields.append("latitude")

        if item_data.longitude is not None:
            item.longitude = item_data.longitude
            update_fields.append("longitude")

        if item_data.tags is not None:
            item.tags = item_data.tags
            update_fields.append("tags")

        if item_data.attributes is not None:
            item.attributes = item_data.attributes
            update_fields.append("attributes")

        if item_data.trade_for is not None:
            item.trade_for = item_data.trade_for
            update_fields.append("trade_for")

        if item_data.trade_radius_km is not None:
            item.trade_radius_km = item_data.trade_radius_km
            update_fields.append("trade_radius_km")

        if item_data.shipping_available is not None:
            item.shipping_available = item_data.shipping_available
            update_fields.append("shipping_available")

        if item_data.local_pickup_only is not None:
            item.local_pickup_only = item_data.local_pickup_only
            update_fields.append("local_pickup_only")

        if item_data.meta_title is not None:
            item.meta_title = item_data.meta_title
            update_fields.append("meta_title")

        if item_data.meta_description is not None:
            item.meta_description = item_data.meta_description
            update_fields.append("meta_description")

        if update_fields:
            await item.save(update_fields=update_fields)
            logger.info(f"Item updated: {item.title} by user {user_id}")

        return item

    @staticmethod
    async def delete_item(item_id: int, user_id: int) -> bool:
        """Soft delete an item."""
        item = await ItemService.get_item_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

        # Check ownership or management permission
        if item.owner_id != user_id:
            has_manage_perm = await RBACService.has_permission(user_id, "item:manage")
            if not has_manage_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own items",
                )

        item.deleted_at = datetime.now(timezone.utc)
        await item.save(update_fields=["deleted_at"])

        logger.info(f"Item deleted: {item.title} by user {user_id}")
        return True

    @staticmethod
    async def search_items(search_data: ItemSearchRequest) -> Tuple[List[Item], int]:
        """Search and filter items."""
        query = Item.filter(deleted_at__isnull=True).prefetch_related(
            "owner", "category"
        )

        # Text search
        if search_data.query:
            query = (
                query.filter(title__icontains=search_data.query)
                | query.filter(description__icontains=search_data.query)
                | query.filter(tags__contains=[search_data.query])
            )

        # Category filter
        if search_data.category_id:
            query = query.filter(category_id=search_data.category_id)

        # Condition filter
        if search_data.condition:
            query = query.filter(condition=search_data.condition)

        # Status filter
        if search_data.status:
            query = query.filter(status=search_data.status)

        # Owner filter
        if search_data.owner_id:
            query = query.filter(owner_id=search_data.owner_id)

        # Location filters
        if search_data.city:
            query = query.filter(city__icontains=search_data.city)

        if search_data.state:
            query = query.filter(state__icontains=search_data.state)

        if search_data.country:
            query = query.filter(country__icontains=search_data.country)

        # Radius search
        if search_data.latitude and search_data.longitude and search_data.radius_km:
            # Simple bounding box approximation for radius search
            lat_diff = (
                search_data.radius_km / 111.0
            )  # Approximate km per degree latitude
            lon_diff = search_data.radius_km / (
                111.0 * math.cos(math.radians(search_data.latitude))
            )

            query = query.filter(
                latitude__gte=search_data.latitude - lat_diff,
                latitude__lte=search_data.latitude + lat_diff,
                longitude__gte=search_data.longitude - lon_diff,
                longitude__lte=search_data.longitude + lon_diff,
            )

        # Price filters
        if search_data.min_value:
            query = query.filter(estimated_value__gte=search_data.min_value)

        if search_data.max_value:
            query = query.filter(estimated_value__lte=search_data.max_value)

        if search_data.currency:
            query = query.filter(currency=search_data.currency)

        # Trade preference filters
        if search_data.shipping_available is not None:
            query = query.filter(shipping_available=search_data.shipping_available)

        if search_data.local_pickup_only is not None:
            query = query.filter(local_pickup_only=search_data.local_pickup_only)

        # Tags filter
        if search_data.tags:
            for tag in search_data.tags:
                query = query.filter(tags__contains=[tag])

        # Get total count
        total = await query.count()

        # Sorting
        sort_field = search_data.sort_by
        if search_data.sort_order == "desc":
            sort_field = f"-{sort_field}"

        # Pagination
        offset = (search_data.page - 1) * search_data.per_page
        items = (
            await query.order_by(sort_field).offset(offset).limit(search_data.per_page)
        )

        return list(items), total

    @staticmethod
    async def get_user_items(
        user_id: int, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Item], int]:
        """Get items owned by a user."""
        query = Item.filter(owner_id=user_id, deleted_at__isnull=True).prefetch_related(
            "category"
        )

        total = await query.count()
        offset = (page - 1) * per_page
        items = await query.order_by("-created_at").offset(offset).limit(per_page)

        return list(items), total

    @staticmethod
    async def get_item_stats() -> ItemStatsResponse:
        """Get overall item statistics."""
        total_items = await Item.filter(deleted_at__isnull=True).count()
        available_items = await Item.filter(
            status=ItemStatus.AVAILABLE, deleted_at__isnull=True
        ).count()
        reserved_items = await Item.filter(
            status=ItemStatus.RESERVED, deleted_at__isnull=True
        ).count()
        traded_items = await Item.filter(
            status=ItemStatus.TRADED, deleted_at__isnull=True
        ).count()

        # Aggregate statistics - using Tortoise ORM aggregation
        total_views = await Item.filter(deleted_at__isnull=True).sum("view_count")
        total_favorites = await Item.filter(deleted_at__isnull=True).sum(
            "favorite_count"
        )
        total_trade_offers = await Item.filter(deleted_at__isnull=True).sum(
            "trade_offer_count"
        )

        # Calculate average value manually
        items_with_value = await Item.filter(
            deleted_at__isnull=True, estimated_value__isnull=False
        ).values_list("estimated_value", flat=True)

        average_value = None
        if items_with_value:
            total_value = sum(items_with_value)
            average_value = total_value / len(items_with_value)

        return ItemStatsResponse(
            total_items=total_items,
            available_items=available_items,
            reserved_items=reserved_items,
            traded_items=traded_items,
            total_views=total_views or 0,
            total_favorites=total_favorites or 0,
            total_trade_offers=total_trade_offers or 0,
            average_value=average_value,
            currency="USD",  # Default currency
        )

    @staticmethod
    async def increment_view_count(item_id: int) -> bool:
        """Increment item view count."""
        item = await Item.filter(id=item_id, deleted_at__isnull=True).first()
        if not item:
            return False

        item.view_count += 1
        item.last_viewed_at = datetime.now(timezone.utc)
        await item.save(update_fields=["view_count", "last_viewed_at"])
        return True

    @staticmethod
    async def bulk_update_items(
        update_data: ItemBulkUpdateRequest, user_id: int
    ) -> int:
        """Bulk update items."""
        # Check if user has management permission
        has_manage_perm = await RBACService.has_permission(user_id, "item:manage")
        if not has_manage_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied: item management required",
            )

        update_fields = {}
        if update_data.status is not None:
            update_fields["status"] = update_data.status
        if update_data.category_id is not None:
            update_fields["category_id"] = update_data.category_id
        if update_data.tags is not None:
            update_fields["tags"] = update_data.tags

        if not update_fields:
            return 0

        updated_count = await Item.filter(
            id__in=update_data.item_ids, deleted_at__isnull=True
        ).update(**update_fields)

        logger.info(f"Bulk updated {updated_count} items by user {user_id}")
        return updated_count

    @staticmethod
    async def duplicate_item(
        item_id: int, duplicate_data: ItemDuplicateRequest, user_id: int
    ) -> Item:
        """Duplicate an item."""
        original_item = await ItemService.get_item_by_id(item_id)
        if not original_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

        # Check ownership or management permission
        if original_item.owner_id != user_id:
            has_manage_perm = await RBACService.has_permission(user_id, "item:manage")
            if not has_manage_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only duplicate your own items",
                )

        # Generate new title
        new_title = duplicate_data.title or f"{original_item.title} (Copy)"

        # Create duplicated item
        duplicated_item = await Item.create(
            title=new_title,
            description=duplicate_data.description or original_item.description,
            condition=original_item.condition,
            owner_id=user_id,
            category_id=original_item.category_id,
            estimated_value=original_item.estimated_value,
            currency=original_item.currency,
            weight_kg=original_item.weight_kg,
            length_cm=original_item.length_cm,
            width_cm=original_item.width_cm,
            height_cm=original_item.height_cm,
            city=original_item.city,
            state=original_item.state,
            country=original_item.country,
            latitude=original_item.latitude,
            longitude=original_item.longitude,
            tags=original_item.tags,
            attributes=original_item.attributes,
            trade_for=original_item.trade_for,
            trade_radius_km=original_item.trade_radius_km,
            shipping_available=original_item.shipping_available,
            local_pickup_only=original_item.local_pickup_only,
            meta_title=duplicate_data.title or original_item.meta_title,
            meta_description=original_item.meta_description,
            status=duplicate_data.status,
            slug=ItemService._generate_slug(new_title),
        )

        logger.info(
            f"Item duplicated: {original_item.title} -> {duplicated_item.title} by user {user_id}"
        )
        return duplicated_item

    @staticmethod
    def _generate_slug(title: str) -> str:
        """Generate a URL-friendly slug from title."""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        slug = slug.strip("-")

        # Ensure slug is not empty
        if not slug:
            slug = "item"

        return slug
