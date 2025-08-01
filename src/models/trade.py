from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
import enum
from decimal import Decimal


class TradeStatus(str, enum.Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"
    DISPUTED = "disputed"


class TradeType(str, enum.Enum):
    """Trade type enumeration."""
    DIRECT = "direct"  # One item for one item
    MULTI_ITEM = "multi_item"  # Multiple items for multiple items
    COUNTER_OFFER = "counter_offer"  # Counter offer to existing trade


class Trade(models.Model):
    """Trade model for item-to-item trading with comprehensive management."""
    
    id = fields.IntField(pk=True)
    
    # Basic trade information
    trade_type = fields.CharEnumField(TradeType, default=TradeType.DIRECT, index=True)
    status = fields.CharEnumField(TradeStatus, default=TradeStatus.PENDING, index=True)
    
    # Relationships
    initiator = fields.ForeignKeyField(
        "models.User", 
        related_name="initiated_trades", 
        on_delete=fields.CASCADE,
        index=True
    )
    recipient = fields.ForeignKeyField(
        "models.User", 
        related_name="received_trades", 
        on_delete=fields.CASCADE,
        index=True
    )
    
    # Trade details
    title = fields.CharField(max_length=255, null=True)
    message = fields.TextField(null=True)
    estimated_value_initiator = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    estimated_value_recipient = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    currency = fields.CharField(max_length=3, default="USD")
    
    # Location and meeting
    meeting_location = fields.CharField(max_length=500, null=True)
    meeting_latitude = fields.FloatField(null=True)
    meeting_longitude = fields.FloatField(null=True)
    meeting_date = fields.DatetimeField(null=True)
    
    # Trade preferences
    shipping_required = fields.BooleanField(default=False)
    local_meetup_only = fields.BooleanField(default=True)
    allow_counter_offers = fields.BooleanField(default=True)
    
    # Timestamps and deadlines
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    expires_at = fields.DatetimeField(null=True, index=True)
    accepted_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    cancelled_at = fields.DatetimeField(null=True)
    
    # Statistics
    view_count = fields.IntField(default=0)
    counter_offer_count = fields.IntField(default=0)
    
    # Soft delete
    deleted_at = fields.DatetimeField(null=True, index=True)
    
    class Meta:
        table = "trades"
        indexes = [
            ("initiator_id", "status"),
            ("recipient_id", "status"),
            ("status", "created_at"),
            ("expires_at", "status"),
            ("trade_type", "status"),
        ]
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Trade(id={self.id}, initiator_id={self.initiator_id}, recipient_id={self.recipient_id}, status='{self.status}')"
    
    @property
    def is_active(self) -> bool:
        """Check if trade is active."""
        return self.status in [TradeStatus.PENDING, TradeStatus.ACCEPTED] and not self.deleted_at
    
    @property
    def is_expired(self) -> bool:
        """Check if trade has expired."""
        if not self.expires_at:
            return False
        from datetime import datetime
        return datetime.now() > self.expires_at
    
    @property
    def days_until_expiry(self) -> int:
        """Get days until trade expires."""
        if not self.expires_at:
            return None
        from datetime import datetime
        delta = self.expires_at - datetime.now()
        return delta.days
    
    async def get_initiator_items(self):
        """Get items offered by the initiator."""
        return await TradeItem.filter(trade_id=self.id, side="initiator").prefetch_related("item")
    
    async def get_recipient_items(self):
        """Get items offered by the recipient."""
        return await TradeItem.filter(trade_id=self.id, side="recipient").prefetch_related("item")
    
    async def get_all_items(self):
        """Get all items in the trade."""
        return await TradeItem.filter(trade_id=self.id).prefetch_related("item")
    
    async def get_counter_offers(self):
        """Get counter offers for this trade."""
        return await Trade.filter(
            trade_type=TradeType.COUNTER_OFFER,
            parent_trade_id=self.id
        ).order_by("-created_at")
    
    async def accept(self):
        """Accept the trade."""
        self.status = TradeStatus.ACCEPTED
        self.accepted_at = fields.timezone.now()
        await self.save(update_fields=["status", "accepted_at"])
        
        # Update item statuses
        trade_items = await self.get_all_items()
        for trade_item in trade_items:
            if trade_item.item:
                trade_item.item.status = "reserved"
                await trade_item.item.save(update_fields=["status"])
    
    async def reject(self):
        """Reject the trade."""
        self.status = TradeStatus.REJECTED
        await self.save(update_fields=["status"])
    
    async def cancel(self):
        """Cancel the trade."""
        self.status = TradeStatus.CANCELLED
        self.cancelled_at = fields.timezone.now()
        await self.save(update_fields=["status", "cancelled_at"])
    
    async def complete(self):
        """Mark the trade as completed."""
        self.status = TradeStatus.COMPLETED
        self.completed_at = fields.timezone.now()
        await self.save(update_fields=["status", "completed_at"])
        
        # Update user statistics
        self.initiator.successful_trades += 1
        self.initiator.total_trades += 1
        await self.initiator.save(update_fields=["successful_trades", "total_trades"])
        
        self.recipient.successful_trades += 1
        self.recipient.total_trades += 1
        await self.recipient.save(update_fields=["successful_trades", "total_trades"])


class TradeItem(models.Model):
    """TradeItem model for managing items in a trade."""
    
    id = fields.IntField(pk=True)
    
    # Relationships
    trade = fields.ForeignKeyField(
        "models.Trade", 
        related_name="trade_items", 
        on_delete=fields.CASCADE,
        index=True
    )
    item = fields.ForeignKeyField(
        "models.Item", 
        related_name="trade_items", 
        on_delete=fields.CASCADE,
        index=True
    )
    
    # Trade side (initiator or recipient)
    side = fields.CharField(max_length=20, choices=[("initiator", "Initiator"), ("recipient", "Recipient")], index=True)
    
    # Additional trade-specific information
    notes = fields.TextField(null=True)
    estimated_value = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "trade_items"
        indexes = [
            ("trade_id", "side"),
            ("item_id", "trade_id"),
        ]
        unique_together = [("trade_id", "item_id")]
    
    def __str__(self):
        return f"TradeItem(id={self.id}, trade_id={self.trade_id}, item_id={self.item_id}, side='{self.side}')"


# Pydantic models for API
Trade_Pydantic = pydantic_model_creator(Trade, name="Trade", exclude=("deleted_at",))
TradeIn_Pydantic = pydantic_model_creator(
    Trade, 
    name="TradeIn", 
    exclude_readonly=True,
    exclude=("deleted_at", "view_count", "counter_offer_count", "accepted_at", "completed_at", "cancelled_at")
)
TradeUpdate_Pydantic = pydantic_model_creator(
    Trade, 
    name="TradeUpdate", 
    exclude_readonly=True,
    exclude=("deleted_at", "view_count", "counter_offer_count", "accepted_at", "completed_at", "cancelled_at", "initiator_id", "recipient_id")
)

TradeItem_Pydantic = pydantic_model_creator(TradeItem, name="TradeItem")
TradeItemIn_Pydantic = pydantic_model_creator(
    TradeItem, 
    name="TradeItemIn", 
    exclude_readonly=True
) 