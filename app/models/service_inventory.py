from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, text


class ServiceInventoryBase(SQLModel):
    service_id: UUID
    inventory_item_id: UUID
    quantity_required: int


class ServiceInventory(ServiceInventoryBase, table=True):
    __tablename__ = "service_inventory"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')")
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')")
        ),
    )


class ServiceInventoryCreate(ServiceInventoryBase):
    pass


class ServiceInventoryUpdate(SQLModel):
    quantity_required: Optional[int] = None
