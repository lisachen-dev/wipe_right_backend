import uuid
from mixins import TimestampMixin
from sqlmodel import Field

class ProviderInventory (TimestampMixin, table=True):
    __tablename__ = "provider_inventory"
    provider: uuid.UUID = Field(foreign_key="providers.id", nullable=False)
    inventory_item_id: uuid.UUID = Field(foreign_key="inventory_items.id", nullable=False)
    quantity_available: int = Field(nullable=False)