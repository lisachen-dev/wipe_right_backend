from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, text

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.provider import Provider


class ReviewBase(SQLModel):
    rating: int = Field(default=5, ge=1, le=5)
    description: Optional[str] = None


class Review(ReviewBase, table=True):
    __tablename__ = "reviews"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    customer_id: UUID = Field(foreign_key="customers.id")
    provider_id: UUID = Field(foreign_key="providers.id")
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

    provider: "Provider" = Relationship(back_populates="reviews")
    customer: "Customer" = Relationship(back_populates="reviews")


class ReviewCreate(ReviewBase):
    customer_id: UUID
    provider_id: UUID


class ReviewUpdate(SQLModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    description: Optional[str] = None


class ReviewRead(ReviewBase):
    created_at: Optional[datetime]
    customer_name: str
