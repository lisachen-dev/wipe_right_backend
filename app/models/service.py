import uuid
from typing import Optional
from sqlmodel import Field
from mixins import TimestampMixin

class Service(TimestampMixin, table=True):
    __tablename__ = "services"

    provider_id: uuid.UUID = Field(foreign_key="providers.id", nullable=False)
    service_title: str = Field(nullable=False)
    service_description: Optional[str] = None
    pricing: float = Field(nullable=False)
    duration: int = Field(nullable=False)
