import enum

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinLengthValidator


class ImageStatus(str, enum.Enum):
    """Image status enumeration."""

    ACTIVE = "active"
    PROCESSING = "processing"
    FAILED = "failed"
    DELETED = "deleted"


class ItemImage(models.Model):
    """ItemImage model for storing item images with comprehensive metadata."""

    id = fields.IntField(pk=True)

    # Relationships
    item = fields.ForeignKeyField(
        "models.Item", related_name="images", on_delete=fields.CASCADE, index=True
    )

    # File information
    image_url = fields.CharField(max_length=500, validators=[MinLengthValidator(1)])
    thumbnail_url = fields.CharField(max_length=500, null=True)
    original_filename = fields.CharField(max_length=255, null=True)
    file_size_bytes = fields.BigIntField(null=True)

    # Image metadata
    width = fields.IntField(null=True)
    height = fields.IntField(null=True)
    format = fields.CharField(max_length=10, null=True)  # jpg, png, webp, etc.
    mime_type = fields.CharField(max_length=100, null=True)

    # Display settings
    is_primary = fields.BooleanField(default=False, index=True)
    sort_order = fields.IntField(default=0, index=True)
    alt_text = fields.CharField(max_length=255, null=True)
    caption = fields.CharField(max_length=500, null=True)

    # Status and processing
    status = fields.CharEnumField(ImageStatus, default=ImageStatus.ACTIVE, index=True)
    processing_error = fields.TextField(null=True)

    # Storage information
    storage_provider = fields.CharField(
        max_length=50, default="local"
    )  # local, s3, cloudinary, etc.
    storage_path = fields.CharField(max_length=500, null=True)
    storage_metadata = fields.JSONField(
        default=dict
    )  # Additional storage-specific metadata

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    processed_at = fields.DatetimeField(null=True)
    deleted_at = fields.DatetimeField(null=True, index=True)

    class Meta:
        table = "item_images"
        indexes = [
            ("item_id", "is_primary"),
            ("item_id", "sort_order"),
            ("status", "created_at"),
            ("storage_provider", "status"),
        ]
        ordering = ["-is_primary", "sort_order", "created_at"]

    def __str__(self):
        return f"ItemImage(id={self.id}, item_id={self.item_id}, is_primary={self.is_primary})"

    @property
    def is_active(self) -> bool:
        """Check if image is active."""
        return self.status == ImageStatus.ACTIVE and not self.deleted_at

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio of the image."""
        if self.width and self.height and self.height > 0:
            return self.width / self.height
        return 1.0

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        if self.file_size_bytes:
            return self.file_size_bytes / (1024 * 1024)
        return 0.0

    @property
    def display_url(self) -> str:
        """Get the display URL (thumbnail if available, otherwise original)."""
        return self.thumbnail_url or self.image_url

    async def set_as_primary(self):
        """Set this image as the primary image for the item."""
        # Remove primary flag from other images of the same item
        await ItemImage.filter(item_id=self.item_id, is_primary=True).update(
            is_primary=False
        )
        # Set this image as primary
        self.is_primary = True
        await self.save(update_fields=["is_primary"])

    async def get_next_sort_order(self) -> int:
        """Get the next sort order for this item's images."""
        max_order = await ItemImage.filter(item_id=self.item_id).aggregate(
            max_order=fields.Max("sort_order")
        )
        return (max_order["max_order"] or 0) + 1


# Pydantic models for API
ItemImage_Pydantic = pydantic_model_creator(
    ItemImage, name="ItemImage", exclude=("deleted_at", "processing_error")
)
ItemImageIn_Pydantic = pydantic_model_creator(
    ItemImage,
    name="ItemImageIn",
    exclude_readonly=True,
    exclude=(
        "deleted_at",
        "processing_error",
        "width",
        "height",
        "format",
        "mime_type",
        "file_size_bytes",
        "processed_at",
    ),
)
ItemImageUpdate_Pydantic = pydantic_model_creator(
    ItemImage,
    name="ItemImageUpdate",
    exclude_readonly=True,
    exclude=(
        "deleted_at",
        "processing_error",
        "width",
        "height",
        "format",
        "mime_type",
        "file_size_bytes",
        "processed_at",
        "item_id",
    ),
)
