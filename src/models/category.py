from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Category(models.Model):
    """Category model for item categorization."""
    
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)
    parent_id = fields.IntField(null=True)  # For hierarchical categories
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "categories"
    
    def __str__(self):
        return f"Category(id={self.id}, name='{self.name}')"


# Pydantic models for API
Category_Pydantic = pydantic_model_creator(Category, name="Category")
CategoryIn_Pydantic = pydantic_model_creator(Category, name="CategoryIn", exclude_readonly=True) 