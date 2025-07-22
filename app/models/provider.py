from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text, Relationship

from app.models.service import ServiceRead
from app.models.reviews import ReviewRead

if TYPE_CHECKING:
    from app.models.service import Service
    from app.models.service import Review

class ProviderBase(SQLModel):
    email: str
    phone_number: Optional[int] = None

# Full model for DB
class Provider(ProviderBase, table=True):
    __tablename__ = "providers"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("(now() AT TIME ZONE 'utc')"))
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("(now() AT TIME ZONE 'utc')"))
    )

    services: list["Service"] = Relationship(back_populates = "provider")
    reviews: list["Review"] = Relationship(back_populates = "provider")


# Schema for create
class ProviderCreate(SQLModel):
    email: str
    phone_number: Optional[int] = None
    user_id: UUID

# Schema for update
class ProviderUpdate(SQLModel):
    email: Optional[str] = None
    phone_number: Optional[int] = None

class ProviderResponseDetail(SQLModel):
    id: UUID
    # name
    email: str
    phone_number: Optional[str] = None
    services: list[ServiceRead]
    reviews: list[ReviewRead]