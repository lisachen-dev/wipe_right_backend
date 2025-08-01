from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import (
    Column,
    DateTime,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
    text,
)

from app.models.enums import StatusEnum

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.booking import Booking
    from app.models.reviews import Review


class CustomerBase(SQLModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


# Full model for DB
class Customer(CustomerBase, table=True):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("supabase_user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    supabase_user_id: UUID = Field(nullable=False, index=True)

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

    reviews: List["Review"] = Relationship(back_populates="customer")
    addresses: List["Address"] = Relationship(back_populates="customer")
    bookings: List["Booking"] = Relationship(back_populates="customer")


# depends on payload schemas
class CustomerCreate(CustomerBase):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: Optional[PhoneNumber] = Field(
        default=None, description="i.e. +1########## or (###) ###-####"
    )


# Schema for update
class CustomerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[PhoneNumber] = Field(
        default=None, description="i.e. +1########## or (###) ###-####"
    )


class CustomerRead(CustomerBase):
    id: UUID


class CurrentBookings(SQLModel):
    provider_first_name: str
    provider_last_name: str
    provider_company_name: str
    status: StatusEnum
    start_time: datetime
    service_title: str
    booking_id: UUID
    provider_id: UUID


class CustomersBookings(SQLModel):
    upcoming_bookings: List[CurrentBookings]
    completed_needs_review: List[CurrentBookings]
