import enum

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinLengthValidator


class CategoryStatus(str, enum.Enum):
    """Category status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    HIDDEN = "hidden"


class Category(models.Model):
    """Category model for item categorization with hierarchical structure."""

    id = fields.IntField(pk=True)

    # Basic fields
    name = fields.CharField(
        max_length=100, unique=True, index=True, validators=[MinLengthValidator(2)]
    )
    slug = fields.CharField(max_length=120, unique=True, index=True)
    description = fields.TextField(null=True)

    # Hierarchical structure
    parent = fields.ForeignKeyField(
        "models.Category", related_name="children", null=True, on_delete=fields.CASCADE
    )
    level = fields.IntField(default=0, index=True)
    path = fields.CharField(max_length=500, null=True)  # For easy querying of full path

    # Metadata
    icon = fields.CharField(max_length=50, null=True)  # Icon class or emoji
    color = fields.CharField(max_length=7, null=True)  # Hex color code
    sort_order = fields.IntField(default=0, index=True)
    status = fields.CharEnumField(
        CategoryStatus, default=CategoryStatus.ACTIVE, index=True
    )

    # Statistics
    item_count = fields.IntField(default=0)
    trade_count = fields.IntField(default=0)

    # SEO
    meta_title = fields.CharField(max_length=255, null=True)
    meta_description = fields.TextField(null=True)
    meta_keywords = fields.CharField(max_length=500, null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True, index=True)

    class Meta:
        table = "categories"
        indexes = [
            ("parent_id", "status"),
            ("level", "sort_order"),
            ("status", "item_count"),
            ("slug", "status"),
        ]
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"Category(id={self.id}, name='{self.name}', level={self.level})"

    @property
    def is_root(self) -> bool:
        """Check if category is a root category."""
        return self.parent_id is None

    @property
    def is_leaf(self) -> bool:
        """Check if category is a leaf category (no children)."""
        return not self.children.exists()

    @property
    def full_path(self) -> str:
        """Get the full category path."""
        if self.path:
            return self.path
        return self.name

    @property
    def breadcrumb(self) -> list:
        """Get breadcrumb trail for this category."""
        breadcrumb = [self]
        current = self
        while current.parent:
            current = current.parent
            breadcrumb.insert(0, current)
        return breadcrumb

    async def get_ancestors(self) -> list:
        """Get all ancestor categories."""
        ancestors = []
        current = self
        while current.parent:
            current = await current.parent
            ancestors.append(current)
        return ancestors

    async def get_descendants(self) -> list:
        """Get all descendant categories."""
        descendants = []
        for child in await self.children.all():
            descendants.append(child)
            descendants.extend(await child.get_descendants())
        return descendants

    async def update_item_count(self):
        """Update the item count for this category."""
        from .item import Item

        count = await Item.filter(category_id=self.id, is_available=True).count()
        self.item_count = count
        await self.save(update_fields=["item_count"])


# Pydantic models for API
Category_Pydantic = pydantic_model_creator(
    Category, name="Category", exclude=("deleted_at",)
)
CategoryIn_Pydantic = pydantic_model_creator(
    Category,
    name="CategoryIn",
    exclude_readonly=True,
    exclude=("deleted_at", "item_count", "trade_count", "level", "path"),
)
CategoryUpdate_Pydantic = pydantic_model_creator(
    Category,
    name="CategoryUpdate",
    exclude_readonly=True,
    exclude=("deleted_at", "item_count", "trade_count", "level", "path"),
)
