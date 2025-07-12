import uuid
from mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field
from datetime import datetime

class Booking (TimestampMixin, table=True):
    __tablename__ = "bookings"

    customer_id: uuid.UUID = Field(foreign_key="customers.id")
    provider_id: uuid.UUID = Field(foreign_key="providers.id")
    service_id: uuid.UUID = Field(foreign_key="services.id")
    special_instructions: Optional[str] = None
    service_notes: Optional[str] = None
    start_time: datetime = Field(nullable=False)