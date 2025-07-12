import uuid
import enum
from mixins import TimestampMixin
from sqlmodel import Field

class PaymentMethodEnum(str, enum.Enum):
    card = "card"

class Transaction(TimestampMixin, table=True):
    __tablename__ = "transactions"

    booking_id: uuid.UUID = Field(foreign_key="bookings.id", nullable=False)
    payment_method: PaymentMethodEnum = Field(nullable=False)