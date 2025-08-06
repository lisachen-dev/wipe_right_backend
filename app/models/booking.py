from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, text

from app.models.address import AddressRead
from app.models.customer import CustomerRead
from app.models.enums import StatusEnum
from app.models.service import ServiceResponseProvider

if TYPE_CHECKING:
    from app.models.address import Address
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
    address_id: UUID = Field(foreign_key="addresses.id")

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
    address: "Address" = Relationship(back_populates="bookings")


class BookingCreate(BookingBase):
    provider_id: UUID
    service_id: UUID
    address_id: UUID
    stripe_payment_id: Optional[str] = Field(default=None)


class BookingUpdate(SQLModel):
    special_instructions: Optional[str] = None
    service_notes: Optional[str] = None
    start_time: Optional[datetime] = None
    stripe_payment_id: Optional[str] = None


class BookingDetails(SQLModel):
    id: UUID
    start_time: datetime
    status: StatusEnum
    provider_company_name: Optional[str] = None
    provider_phone_number: Optional[str] = None
    customer_phone_number: Optional[str] = None
    customer_address: AddressRead


class BookingStatusUpdate(SQLModel):
    status: StatusEnum


class BookingReponseProvider(BookingBase):
    id: UUID
    service: ServiceResponseProvider
    customer: CustomerRead
    address: AddressRead
