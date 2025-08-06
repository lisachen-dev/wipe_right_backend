from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, text

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.customer import Customer


class AddressBase(SQLModel):
    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state: str
    zip: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Address(AddressBase, table=True):
    __tablename__ = "addresses"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="customers.id")
    customer: "Customer" = Relationship(back_populates="addresses")
    bookings: List["Booking"] = Relationship(back_populates="address")

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


class AddressCreate(SQLModel):
    customer_id: UUID
    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state: str
    zip: str


class AddressUpdate(SQLModel):
    street_address_1: Optional[str] = None
    street_address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class AddressRead(AddressBase):
    id: UUID
