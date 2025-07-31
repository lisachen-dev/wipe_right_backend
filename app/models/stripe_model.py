from uuid import UUID

from pydantic import BaseModel


class PaymentIntentCreateRequest(BaseModel):
    service_id: UUID


class PaymentIntentCreateResponse(BaseModel):
    client_secret: str
