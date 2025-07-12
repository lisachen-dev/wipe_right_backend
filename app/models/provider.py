import uuid
from uuid import uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Provider(SQLModel, table=True):
    __tablename__ = "providers"
    id: Optional[uuid.UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str
    phonenumber: Optional[int] = None
    password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow) # postgres fills these
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow) # postgres fills these