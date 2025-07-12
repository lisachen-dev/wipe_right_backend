import uuid
from mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field

class Review (TimestampMixin, table=True):
    __tablename__ = "reviews"

    customer_id: uuid = Field(foreign_key="customers.id", nullable=False)
    provider_id: uuid = Field(foreign_key="providers.id", nullable=False)
    rating: int = Field(default=5, ge=1, le=5)
    description: Optional[str] = Field(default=None)