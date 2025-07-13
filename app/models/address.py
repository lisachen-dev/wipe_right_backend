import uuid
from mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field

class Address (TimestampMixin, table=True):
    __tablename__ = "addresses"

    customer_id: uuid.UUID = Field(foreign_key="customers.id")
    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state: str
    zip: str