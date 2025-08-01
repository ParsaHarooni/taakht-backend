from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class ItemImage(models.Model):
    """ItemImage model for storing item images."""
    
    id = fields.IntField(pk=True)
    item_id = fields.IntField()
    image_url = fields.CharField(max_length=500)
    is_primary = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "item_images"
    
    def __str__(self):
        return f"ItemImage(id={self.id}, item_id={self.item_id})"


# Pydantic models for API
ItemImage_Pydantic = pydantic_model_creator(ItemImage, name="ItemImage")
ItemImageIn_Pydantic = pydantic_model_creator(ItemImage, name="ItemImageIn", exclude_readonly=True) 