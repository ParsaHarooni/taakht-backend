from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from src.models.item import ItemCondition, ItemStatus


class ItemCreateRequest(BaseModel):
    """Schema for creating a new item."""

    title: str = Field(..., min_length=3, max_length=255, description="Item title")
    description: str = Field(..., min_length=10, description="Item description")
    condition: ItemCondition = Field(..., description="Item condition")
    category_id: int = Field(..., description="Category ID")

    # Optional pricing
    estimated_value: Optional[Decimal] = Field(
        None, ge=Decimal("0.01"), description="Estimated value"
    )
    currency: str = Field("USD", max_length=3, description="Currency code")

    # Optional dimensions
    weight_kg: Optional[float] = Field(None, ge=0.0, description="Weight in kilograms")
    length_cm: Optional[float] = Field(
        None, ge=0.0, description="Length in centimeters"
    )
    width_cm: Optional[float] = Field(None, ge=0.0, description="Width in centimeters")
    height_cm: Optional[float] = Field(
        None, ge=0.0, description="Height in centimeters"
    )

    # Optional location
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")

    # Optional attributes
    tags: List[str] = Field(default_factory=list, description="List of tags")
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Custom attributes"
    )

    # Trade preferences
    trade_for: Optional[str] = Field(None, description="What you want to trade for")
    trade_radius_km: int = Field(
        50, ge=1, le=1000, description="Trade radius in kilometers"
    )
    shipping_available: bool = Field(False, description="Whether shipping is available")
    local_pickup_only: bool = Field(True, description="Local pickup only")

    # SEO
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    meta_description: Optional[str] = Field(None, description="SEO description")


class ItemUpdateRequest(BaseModel):
    """Schema for updating an item."""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    condition: Optional[ItemCondition] = None
    category_id: Optional[int] = None
    status: Optional[ItemStatus] = None

    # Optional pricing
    estimated_value: Optional[Decimal] = Field(None, ge=Decimal("0.01"))
    currency: Optional[str] = Field(None, max_length=3)

    # Optional dimensions
    weight_kg: Optional[float] = Field(None, ge=0.0)
    length_cm: Optional[float] = Field(None, ge=0.0)
    width_cm: Optional[float] = Field(None, ge=0.0)
    height_cm: Optional[float] = Field(None, ge=0.0)

    # Optional location
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Optional attributes
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None

    # Trade preferences
    trade_for: Optional[str] = None
    trade_radius_km: Optional[int] = Field(None, ge=1, le=1000)
    shipping_available: Optional[bool] = None
    local_pickup_only: Optional[bool] = None

    # SEO
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None


class ItemResponse(BaseModel):
    """Schema for item response."""

    id: int
    title: str
    description: str
    condition: ItemCondition
    status: ItemStatus
    owner_id: int
    category_id: Optional[int]
    estimated_value: Optional[Decimal]
    currency: str
    weight_kg: Optional[float]
    length_cm: Optional[float]
    width_cm: Optional[float]
    height_cm: Optional[float]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    tags: List[str]
    attributes: Dict[str, Any]
    trade_for: Optional[str]
    trade_radius_km: int
    shipping_available: bool
    local_pickup_only: bool
    view_count: int
    favorite_count: int
    trade_offer_count: int
    slug: str
    meta_title: Optional[str]
    meta_description: Optional[str]
    created_at: datetime
    updated_at: datetime
    listed_at: datetime
    last_viewed_at: Optional[datetime]

    # Owner information
    owner_username: Optional[str] = None
    owner_full_name: Optional[str] = None

    # Category information
    category_name: Optional[str] = None

    # Computed properties
    is_available: bool
    dimensions: Dict[str, Optional[float]]
    location: Dict[str, Optional[str]]

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """Schema for item list response."""

    items: List[ItemResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ItemSearchRequest(BaseModel):
    """Schema for item search request."""

    query: Optional[str] = Field(None, description="Search query")
    category_id: Optional[int] = Field(None, description="Filter by category")
    condition: Optional[ItemCondition] = Field(None, description="Filter by condition")
    status: Optional[ItemStatus] = Field(None, description="Filter by status")
    owner_id: Optional[int] = Field(None, description="Filter by owner")

    # Location filters
    city: Optional[str] = Field(None, description="Filter by city")
    state: Optional[str] = Field(None, description="Filter by state")
    country: Optional[str] = Field(None, description="Filter by country")
    latitude: Optional[float] = Field(
        None, description="Center latitude for radius search"
    )
    longitude: Optional[float] = Field(
        None, description="Center longitude for radius search"
    )
    radius_km: Optional[float] = Field(
        None, ge=0.1, le=1000, description="Search radius in kilometers"
    )

    # Price filters
    min_value: Optional[Decimal] = Field(
        None, ge=Decimal("0"), description="Minimum estimated value"
    )
    max_value: Optional[Decimal] = Field(
        None, ge=Decimal("0"), description="Maximum estimated value"
    )
    currency: Optional[str] = Field(
        None, max_length=3, description="Currency for price filters"
    )

    # Trade preferences
    shipping_available: Optional[bool] = Field(
        None, description="Filter by shipping availability"
    )
    local_pickup_only: Optional[bool] = Field(
        None, description="Filter by pickup preference"
    )

    # Tags
    tags: Optional[List[str]] = Field(None, description="Filter by tags")

    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

    # Sorting
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        valid_fields = [
            "created_at",
            "updated_at",
            "listed_at",
            "title",
            "estimated_value",
            "view_count",
            "favorite_count",
            "trade_offer_count",
        ]
        if v not in valid_fields:
            raise ValueError(f"Invalid sort field. Must be one of: {valid_fields}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class ItemStatsResponse(BaseModel):
    """Schema for item statistics response."""

    total_items: int
    available_items: int
    reserved_items: int
    traded_items: int
    total_views: int
    total_favorites: int
    total_trade_offers: int
    average_value: Optional[Decimal]
    currency: str


class ItemFavoriteRequest(BaseModel):
    """Schema for favoriting/unfavoriting an item."""

    action: str = Field(..., description="Action: 'add' or 'remove'")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        if v not in ["add", "remove"]:
            raise ValueError('Action must be "add" or "remove"')
        return v


class ItemBulkUpdateRequest(BaseModel):
    """Schema for bulk updating items."""

    item_ids: List[int] = Field(..., description="List of item IDs to update")
    status: Optional[ItemStatus] = Field(None, description="New status for all items")
    category_id: Optional[int] = Field(None, description="New category for all items")
    tags: Optional[List[str]] = Field(None, description="New tags for all items")


class ItemDuplicateRequest(BaseModel):
    """Schema for duplicating an item."""

    title: Optional[str] = Field(
        None, description="New title (if not provided, will append 'Copy')"
    )
    description: Optional[str] = Field(None, description="New description")
    status: ItemStatus = Field(
        ItemStatus.AVAILABLE, description="Status for the duplicated item"
    )
