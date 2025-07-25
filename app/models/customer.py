from typing import Optional, TYPE_CHECKING, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text, Relationship, UniqueConstraint

if TYPE_CHECKING:
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

    supabase_user_id: UUID = Field(nullable=False, index=True, foreign_key="auth.users.id")

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

    reviews: List["Review"] = Relationship(back_populates="customer")


# depends on payload schemas
class CustomerCreate(CustomerBase):
    pass

# Schema for update
class CustomerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
