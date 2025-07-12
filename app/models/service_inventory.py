import uuid
from mixins import TimestampMixin
from sqlmodel import Field

class ServiceInventory(TimestampMixin, table=True):
    __tablename__ = "service_inventory"

    service_id: uuid.UUID = Field(foreign_key="services.id", nullable=False)
    inventory_item_id: uuid.UUID = Field(foreign_key="inventory_items.id", nullable=False)
    quantity_required: int = Field(nullable=False)