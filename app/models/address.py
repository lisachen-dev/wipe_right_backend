from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, text, Relationship

if TYPE_CHECKING:
    from app.models.customer import Customer


class AddressBase(SQLModel):
    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state: str
    zip: str


class Address(AddressBase, table=True):
    __tablename__ = "addresses"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="customers.id")

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

    customer: "Customer" = Relationship(back_populates="addresses")


class AddressCreate(AddressBase):
    customer_id: UUID


class AddressUpdate(SQLModel):
    street_address_1: Optional[str] = None
    street_address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
