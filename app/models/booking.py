from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, text


class BookingBase(SQLModel):
    special_instructions: Optional[str] = None
    service_notes: Optional[str] = None
    start_time: datetime


class Booking(BookingBase, table=True):
    __tablename__ = "bookings"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    customer_id: UUID = Field(foreign_key="customers.id")
    provider_id: UUID = Field(foreign_key="providers.id")
    service_id: UUID = Field(foreign_key="services.id")

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


class BookingCreate(BookingBase):
    customer_id: UUID
    provider_id: UUID
    service_id: UUID


class BookingUpdate(SQLModel):
    special_instructions: Optional[str] = None
    service_notes: Optional[str] = None
    start_time: Optional[datetime] = None
