from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Item(models.Model):
    """Item model for trading items."""
    
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    condition = fields.CharField(max_length=50)  # new, like_new, good, fair, poor
    category_id = fields.IntField()
    owner_id = fields.IntField()
    is_available = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "items"
    
    def __str__(self):
        return f"Item(id={self.id}, title='{self.title}')"


# Pydantic models for API
Item_Pydantic = pydantic_model_creator(Item, name="Item")
ItemIn_Pydantic = pydantic_model_creator(Item, name="ItemIn", exclude_readonly=True) 