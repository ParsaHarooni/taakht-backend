import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.middlewares.auth import get_current_active_user, get_optional_user
from src.middlewares.rbac import (
    get_user_with_permission,
    require_item_manage,
)
from src.models.item import ItemStatus
from src.models.user import User
from src.schemas.item import (
    ItemBulkUpdateRequest,
    ItemCreateRequest,
    ItemDuplicateRequest,
    ItemFavoriteRequest,
    ItemListResponse,
    ItemResponse,
    ItemSearchRequest,
    ItemStatsResponse,
    ItemUpdateRequest,
)
from src.services.item import ItemService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/items", tags=["items"])


# Item CRUD Endpoints
@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreateRequest, current_user: User = Depends(get_current_active_user)
):
    """Create a new item."""
    item = await ItemService.create_item(item_data, current_user.id)

    # Get full item with related data
    full_item = await ItemService.get_item_by_id(item.id)
    return ItemResponse.from_orm(full_item)


@router.get("/", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ItemStatus] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    owner_id: Optional[int] = Query(None, description="Filter by owner"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List items with basic filtering."""
    # Build search request
    search_data = ItemSearchRequest(
        page=page,
        per_page=per_page,
        status=status,
        category_id=category_id,
        owner_id=owner_id,
    )

    items, total = await ItemService.search_items(search_data)

    total_pages = (total + per_page - 1) // per_page

    return ItemListResponse(
        items=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/search", response_model=ItemListResponse)
async def search_items(
    search_data: ItemSearchRequest,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Advanced item search with multiple filters."""
    items, total = await ItemService.search_items(search_data)

    total_pages = (total + search_data.per_page - 1) // search_data.per_page

    return ItemListResponse(
        items=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=search_data.page,
        per_page=search_data.per_page,
        total_pages=total_pages,
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int = Path(..., description="Item ID"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get a specific item by ID."""
    item = await ItemService.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Increment view count if user is authenticated
    if current_user:
        await ItemService.increment_view_count(item_id)

    return ItemResponse.from_orm(item)


@router.get("/slug/{slug}", response_model=ItemResponse)
async def get_item_by_slug(
    slug: str = Path(..., description="Item slug"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get a specific item by slug."""
    item = await ItemService.get_item_by_slug(slug)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    # Increment view count if user is authenticated
    if current_user:
        await ItemService.increment_view_count(item.id)

    return ItemResponse.from_orm(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int = Path(..., description="Item ID"),
    item_data: ItemUpdateRequest = ...,
    current_user: User = Depends(get_current_active_user),
):
    """Update an item."""
    item = await ItemService.update_item(item_id, item_data, current_user.id)

    # Get full item with related data
    full_item = await ItemService.get_item_by_id(item.id)
    return ItemResponse.from_orm(full_item)


@router.delete("/{item_id}")
async def delete_item(
    item_id: int = Path(..., description="Item ID"),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an item."""
    await ItemService.delete_item(item_id, current_user.id)
    return {"message": "Item deleted successfully"}


# User Items Endpoints
@router.get("/me/items", response_model=ItemListResponse)
async def get_my_items(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's items."""
    items, total = await ItemService.get_user_items(current_user.id, page, per_page)

    total_pages = (total + per_page - 1) // per_page

    return ItemListResponse(
        items=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/users/{user_id}/items", response_model=ItemListResponse)
async def get_user_items(
    user_id: int = Path(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get items owned by a specific user."""
    items, total = await ItemService.get_user_items(user_id, page, per_page)

    total_pages = (total + per_page - 1) // per_page

    return ItemListResponse(
        items=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Item Statistics Endpoints
@router.get("/stats/overview", response_model=ItemStatsResponse)
async def get_item_stats(
    current_user: User = Depends(get_user_with_permission("item:read")),
):
    """Get overall item statistics."""
    return await ItemService.get_item_stats()


# Item Management Endpoints (Admin/Moderator)
@router.post("/bulk-update")
async def bulk_update_items(
    update_data: ItemBulkUpdateRequest,
    current_user: User = Depends(require_item_manage),
):
    """Bulk update items (admin/moderator only)."""
    updated_count = await ItemService.bulk_update_items(update_data, current_user.id)
    return {
        "message": f"Successfully updated {updated_count} items",
        "updated_count": updated_count,
    }


@router.post("/{item_id}/duplicate", response_model=ItemResponse)
async def duplicate_item(
    item_id: int = Path(..., description="Item ID to duplicate"),
    duplicate_data: ItemDuplicateRequest = ...,
    current_user: User = Depends(get_current_active_user),
):
    """Duplicate an item."""
    duplicated_item = await ItemService.duplicate_item(
        item_id, duplicate_data, current_user.id
    )

    # Get full item with related data
    full_item = await ItemService.get_item_by_id(duplicated_item.id)
    return ItemResponse.from_orm(full_item)


# Item Status Management
@router.patch("/{item_id}/status")
async def update_item_status(
    item_id: int = Path(..., description="Item ID"),
    status: ItemStatus = Query(..., description="New status"),
    current_user: User = Depends(get_current_active_user),
):
    """Update item status."""
    item_data = ItemUpdateRequest(status=status)
    item = await ItemService.update_item(item_id, item_data, current_user.id)

    return {
        "message": f"Item status updated to {status}",
        "item_id": item.id,
        "status": status,
    }


# Item Favorites (placeholder for future implementation)
@router.post("/{item_id}/favorite")
async def toggle_item_favorite(
    item_id: int = Path(..., description="Item ID"),
    favorite_data: ItemFavoriteRequest = ...,
    current_user: User = Depends(get_current_active_user),
):
    """Toggle item favorite status (placeholder)."""
    # TODO: Implement favorite functionality
    return {
        "message": f"Favorite {favorite_data.action} for item {item_id}",
        "item_id": item_id,
        "action": favorite_data.action,
    }


# Category Items Endpoints
@router.get("/categories/{category_id}/items", response_model=ItemListResponse)
async def get_category_items(
    category_id: int = Path(..., description="Category ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get items in a specific category."""
    search_data = ItemSearchRequest(
        category_id=category_id, page=page, per_page=per_page
    )

    items, total = await ItemService.search_items(search_data)

    total_pages = (total + per_page - 1) // per_page

    return ItemListResponse(
        items=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Location-based Search
@router.get("/nearby", response_model=ItemListResponse)
async def get_nearby_items(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(
        50, ge=0.1, le=1000, description="Search radius in kilometers"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get items near a specific location."""
    search_data = ItemSearchRequest(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        page=page,
        per_page=per_page,
    )

    items, total = await ItemService.search_items(search_data)

    total_pages = (total + per_page - 1) // per_page

    return ItemListResponse(
        items=[ItemResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Similar Items (placeholder for future implementation)
@router.get("/{item_id}/similar", response_model=ItemListResponse)
async def get_similar_items(
    item_id: int = Path(..., description="Item ID"),
    limit: int = Query(5, ge=1, le=20, description="Number of similar items"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get similar items (placeholder)."""
    # TODO: Implement similar items algorithm
    return ItemListResponse(items=[], total=0, page=1, per_page=limit, total_pages=0)
