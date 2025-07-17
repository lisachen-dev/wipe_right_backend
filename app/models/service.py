from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, text
from enum import Enum

class ServiceEnum( Enum): 
    HOUSE_CLEANING = "House Cleaning"
    LAWN_AND_GARDEN = "Lawn & Garden"
    HANDYMAN_AND_REPAIRS = "Handyman & Repairs"
    EXTERIOR_CLEANING = "Exterior Cleaning"
    SPECIALIZED_CLEANING = "Specialized Cleaning"
    ASSEMBLY_AND_INSTALLATION = "Assembly & Installation"


class ServiceBase(SQLModel):
    service_title: str
    service_description: Optional[str] = None
    pricing: float
    duration: int  # in minutes
    category: str

class Service(ServiceBase, table=True):
    __tablename__ = "services"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    provider_id: UUID = Field(foreign_key="providers.id", nullable=False)

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')"))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')"))
    )

class ServiceCreate(ServiceBase):
    provider_id: UUID

class ServiceUpdate(SQLModel):
    service_title: Optional[str] = None
    service_description: Optional[str] = None
    pricing: Optional[float] = None
    duration: Optional[int] = None
