from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Trade(models.Model):
    """Trade model for item-to-item trading."""
    
    id = fields.IntField(pk=True)
    initiator_id = fields.IntField()
    recipient_id = fields.IntField()
    status = fields.CharField(max_length=20, default="pending")  # pending, accepted, rejected, cancelled, completed
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "trades"
    
    def __str__(self):
        return f"Trade(id={self.id}, status='{self.status}')"


# Pydantic models for API
Trade_Pydantic = pydantic_model_creator(Trade, name="Trade")
TradeIn_Pydantic = pydantic_model_creator(Trade, name="TradeIn", exclude_readonly=True) 