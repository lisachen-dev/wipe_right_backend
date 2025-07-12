from mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field

class InventoryItems (TimestampMixin, table=True):
    __tablename__ = "inventory_items"

    item_name: str = Field(nullable=False)
    description: Optional[str] = None
    unit: Optional[str] = Field(default = None) # e.g., "bottle", "piece"
    cost: float = Field(nullable=False)