from typing import Optional
from uuid import UUID
from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text

class InventoryItemsBase(SQLModel):
    item_name: str
    description: Optional[str] = None
    unit: Optional[str] = None # e.g., "bottle", "piece"
    cost: float

class InventoryItems (InventoryItemsBase, table=True):
    __tablename__ = "inventory_items"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("(now() AT TIME ZONE 'utc')"))
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("(now() AT TIME ZONE 'utc')"))
    )

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