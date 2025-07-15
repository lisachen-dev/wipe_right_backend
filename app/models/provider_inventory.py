import uuid
from sqlmodel import SQLModel, Field

class ProviderInventory (SQLModel, table=True):
    __tablename__ = "provider_inventory"

    provider: uuid.UUID
    inventory_item_id: uuid.UUID
    quantity_available: int

class ProviderInventoryCreate(SQLModel):
    inventory_item_id: uuid.UUID
    quantity_available: int = Field(gt=0)

class ProviderInventoryUpdate(SQLModel):
    quantity_available: int