from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PaymentIntentCreateRequest(BaseModel):
    service_id: UUID
    coupon_code: Optional[str] = None


class PaymentIntentCreateResponse(BaseModel):
    client_secret: str
