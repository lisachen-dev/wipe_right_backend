import uuid
from uuid import uuid4
from typing import Optional
from sqlmodel import SQLModel, Field, Column, DateTime, text
from datetime import datetime

class TimestampMixin (SQLModel):
    id: Optional[uuid.UUID] = Field(default_factory=uuid4, primary_key=True)
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