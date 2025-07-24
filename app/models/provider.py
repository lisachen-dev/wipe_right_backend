from typing import Optional, TYPE_CHECKING, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text, UniqueConstraint, Relationship

from app.models.service import ServiceRead
from app.models.reviews import ReviewRead

if TYPE_CHECKING:
    from app.models.service import Service
    from app.models.reviews import Review


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

    supabase_user_id: UUID = Field(nullable=False, index=True, foreign_key="auth.users.id")

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')")))

    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')")))

    services: List["Service"] = Relationship(back_populates="provider")
    reviews: List["Review"] = Relationship(back_populates="provider")


# depends on payload schemas
class ProviderCreate(ProviderBase):
    pass


# Schema for update
class ProviderUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None


class ProviderResponseDetail(SQLModel):
    id: UUID
    phone_number: Optional[str] = None
    services: list[ServiceRead]
    reviews: list[ReviewRead]
    review_count: int
    average_rating: Optional[float] = None


class ProviderCategoryResponse(SQLModel):
    id: UUID
    company_name: Optional[str] = None
    first_name: str
    last_name: str
