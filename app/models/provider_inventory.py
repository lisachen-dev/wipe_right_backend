from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text

class ProviderInventoryBase(SQLModel):
    quantity_available: int

class ProviderInventory (ProviderInventoryBase, table=True):
    __tablename__ = "provider_inventory"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    supabase_user_id: UUID = Field(nullable=False, index=True, foreign_key="auth.users.id")
     provider_id: UUID = Field(nullable=False, foreign_key="providers.id", index=True)
    inventory_item_id: UUID

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

class ProviderInventoryCreate(SQLModel):
    inventory_item_id: UUID
    quantity_available: int = Field(gt=0)

class ProviderInventoryUpdate(SQLModel):
    quantity_available: int