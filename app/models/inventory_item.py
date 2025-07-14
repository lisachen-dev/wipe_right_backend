import uuid

from app.models.mixins import TimestampMixin
from typing import Optional
from sqlmodel import SQLModel, Field

class InventoryItemsBase (TimestampMixin, table=True):
    __tablename__ = "inventory_items"

    item_name: str
    description: Optional[str] = None
    unit: Optional[str] = None # e.g., "bottle", "piece"
    cost: float

class InventoryItemCreate(SQLModel):
    item_name: str
    description: Optional[str] = None
    unit: Optional[str] = None # e.g., "bottle", "piece"
    cost: float

class InventoryItemUpdate(SQLModel):
    item_name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    unit: Optional[str] = None
    cost: Optional[float] = Field(default=None, gt=0)