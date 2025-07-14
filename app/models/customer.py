import uuid
from mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field

class Customer (TimestampMixin, table=True):
    __tablename__ = "customers"

    email: str = Field(nullable=False)
    phonenumber: Optional[int] = None
    user_id: uuid.UUID = Field(index=True) # handled in supabase
