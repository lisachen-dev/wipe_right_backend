from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import (
    Column,
    DateTime,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
    text,
)

from app.models.reviews import ReviewRead
from app.models.service import ServiceResponseProvider

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.reviews import Review
    from app.models.service import Service


class ProviderBase(SQLModel):
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone_number: Optional[str] = None


# Full model for DB
class Provider(ProviderBase, table=True):
    __tablename__ = "providers"
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

    services: List["Service"] = Relationship(back_populates="provider")
    reviews: List["Review"] = Relationship(back_populates="provider")
    bookings: List["Booking"] = Relationship(back_populates="provider")


# depends on payload schemas
class ProviderCreate(ProviderBase):
    pass


# Schema for update
class ProviderUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None


class ProviderPublicRead(SQLModel):
    id: UUID
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    services: list[ServiceResponseProvider]


class ProviderResponseDetail(ProviderPublicRead):
    reviews: list[ReviewRead]
    review_count: int
    average_rating: Optional[float] = None
