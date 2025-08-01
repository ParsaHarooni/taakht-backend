from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
import enum
from decimal import Decimal


class ItemCondition(str, enum.Enum):
    """Item condition enumeration."""
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ItemStatus(str, enum.Enum):
    """Item status enumeration."""
    AVAILABLE = "available"
    RESERVED = "reserved"
    TRADED = "traded"
    SOLD = "sold"
    HIDDEN = "hidden"
    DELETED = "deleted"


class Item(models.Model):
    """Item model for trading items with comprehensive details."""
    
    id = fields.IntField(pk=True)
    
    # Basic information
    title = fields.CharField(
        max_length=255, 
        index=True,
        validators=[MinLengthValidator(3)]
    )
    description = fields.TextField()
    condition = fields.CharEnumField(ItemCondition, index=True)
    status = fields.CharEnumField(ItemStatus, default=ItemStatus.AVAILABLE, index=True)
    
    # Relationships
    owner = fields.ForeignKeyField(
        "models.User", 
        related_name="items", 
        on_delete=fields.CASCADE,
        index=True
    )
    category = fields.ForeignKeyField(
        "models.Category", 
        related_name="items", 
        on_delete=fields.PROTECT,
        index=True
    )
    
    # Pricing and valuation (optional for item-to-item trading)
    estimated_value = fields.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = fields.CharField(max_length=3, default="USD")
    
    # Dimensions and weight
    weight_kg = fields.FloatField(null=True, validators=[MinValueValidator(0.0)])
    length_cm = fields.FloatField(null=True, validators=[MinValueValidator(0.0)])
    width_cm = fields.FloatField(null=True, validators=[MinValueValidator(0.0)])
    height_cm = fields.FloatField(null=True, validators=[MinValueValidator(0.0)])
    
    # Location
    city = fields.CharField(max_length=100, null=True, index=True)
    state = fields.CharField(max_length=100, null=True, index=True)
    country = fields.CharField(max_length=100, null=True, index=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    
    # Tags and attributes
    tags = fields.JSONField(default=list)  # List of tag strings
    attributes = fields.JSONField(default=dict)  # Key-value pairs for custom attributes
    
    # Trade preferences
    trade_for = fields.TextField(null=True)  # What the owner wants to trade for
    trade_radius_km = fields.IntField(default=50, validators=[MinValueValidator(1), MaxValueValidator(1000)])
    shipping_available = fields.BooleanField(default=False)
    local_pickup_only = fields.BooleanField(default=True)
    
    # Statistics
    view_count = fields.IntField(default=0, index=True)
    favorite_count = fields.IntField(default=0, index=True)
    trade_offer_count = fields.IntField(default=0)
    
    # SEO and discovery
    slug = fields.CharField(max_length=300, unique=True, index=True)
    meta_title = fields.CharField(max_length=255, null=True)
    meta_description = fields.TextField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    listed_at = fields.DatetimeField(auto_now_add=True, index=True)
    last_viewed_at = fields.DatetimeField(null=True)
    deleted_at = fields.DatetimeField(null=True, index=True)
    
    class Meta:
        table = "items"
        indexes = [
            ("owner_id", "status"),
            ("category_id", "status"),
            ("condition", "status"),
            ("created_at", "status"),
            ("view_count", "status"),
            ("latitude", "longitude"),
            ("city", "state", "country"),
        ]
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Item(id={self.id}, title='{self.title}', owner_id={self.owner_id})"
    
    @property
    def is_available(self) -> bool:
        """Check if item is available for trade."""
        return self.status == ItemStatus.AVAILABLE and not self.deleted_at
    
    @property
    def dimensions(self) -> dict:
        """Get item dimensions as a dictionary."""
        return {
            "length": self.length_cm,
            "width": self.width_cm,
            "height": self.height_cm,
            "weight": self.weight_kg,
        }
    
    @property
    def location(self) -> dict:
        """Get item location as a dictionary."""
        return {
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            } if self.latitude and self.longitude else None,
        }
    
    async def increment_view_count(self):
        """Increment the view count for this item."""
        self.view_count += 1
        self.last_viewed_at = fields.timezone.now()
        await self.save(update_fields=["view_count", "last_viewed_at"])
    
    async def get_primary_image(self):
        """Get the primary image for this item."""
        from .item_image import ItemImage
        return await ItemImage.filter(item_id=self.id, is_primary=True).first()
    
    async def get_all_images(self):
        """Get all images for this item."""
        from .item_image import ItemImage
        return await ItemImage.filter(item_id=self.id).order_by("-is_primary", "created_at")
    
    async def get_similar_items(self, limit: int = 5):
        """Get similar items in the same category."""
        return await Item.filter(
            category_id=self.category_id,
            status=ItemStatus.AVAILABLE,
            id__not=self.id
        ).limit(limit)


# Pydantic models for API
Item_Pydantic = pydantic_model_creator(Item, name="Item", exclude=("deleted_at",))
ItemIn_Pydantic = pydantic_model_creator(
    Item, 
    name="ItemIn", 
    exclude_readonly=True,
    exclude=("deleted_at", "view_count", "favorite_count", "trade_offer_count", "slug")
)
ItemUpdate_Pydantic = pydantic_model_creator(
    Item, 
    name="ItemUpdate", 
    exclude_readonly=True,
    exclude=("deleted_at", "view_count", "favorite_count", "trade_offer_count", "slug", "owner_id")
) 