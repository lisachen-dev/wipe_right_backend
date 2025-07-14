import uuid
from app.models.mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field

class Provider (TimestampMixin, table=True):
    __tablename__ = "providers"

    email: str = Field(nullable=False)
    phonenumber: Optional[int] = None
    user_id: uuid.UUID = Field(index=True) # handled in supabase