from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text, UniqueConstraint

class CustomerBase(SQLModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

# Full model for DB
class Customer(CustomerBase, table=True):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    auth_user_id: UUID = Field(nullable=False, index=True)

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


# depends on payload schemas
class CustomerCreate(CustomerBase):
    pass

# Schema for update
class CustomerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
