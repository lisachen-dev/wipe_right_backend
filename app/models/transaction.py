import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, text


class PaymentMethodEnum(str, enum.Enum):
    card = "card"


class TransactionBase(SQLModel):
    booking_id: UUID
    payment_method: PaymentMethodEnum


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')")
        ),
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'utc')")
        ),
    )


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(SQLModel):
    payment_method: Optional[PaymentMethodEnum] = None
