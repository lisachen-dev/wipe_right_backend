from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, text, Relationship

from app.models.enums import StatusEnum

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.provider import Provider
    from app.models.service import Service


class BookingBase(SQLModel):
    special_instructions: Optional[str] = None
    service_notes: Optional[str] = None
    start_time: datetime
    status: StatusEnum = StatusEnum.confirmed


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

    customer: "Customer" = Relationship(back_populates="bookings")
    provider: "Provider" = Relationship(back_populates="bookings")
    service: "Service" = Relationship(back_populates="bookings")


class BookingCreate(BookingBase):
    customer_id: UUID
    provider_id: UUID
    service_id: UUID


class BookingUpdate(SQLModel):
    special_instructions: Optional[str] = None
    service_notes: Optional[str] = None
    start_time: Optional[datetime] = None
