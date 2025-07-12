from mixins import TimestampMixin
from typing import Optional
from sqlmodel import Field

class Provider (TimestampMixin, table=True):
    __tablename__ = "providers"

    email: str = Field(nullable=False)
    phonenumber: Optional[int] = None
    password: str = Field(nullable=False)