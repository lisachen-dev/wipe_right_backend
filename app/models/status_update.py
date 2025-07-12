import enum
import uuid
from uuid import uuid4
from typing import Optional
from sqlmodel import SQLModel, Field, Column, DateTime, text
from datetime import datetime

class StatusEnum(str, enum.Enum):
    confirmed = "confirmed"
    en_route = "en_route"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class StatusUpdate (SQLModel, table=True):
    __tablename__ = "status_updates"

    id: Optional[uuid.UUID] = Field(default_factory=uuid4, primary_key=True)
    booking_id: uuid = Field(foreign_key="bookings.id", nullable=False)
    status: StatusEnum = Field(nullable=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("(now() AT TIME ZONE 'utc')")
     ))