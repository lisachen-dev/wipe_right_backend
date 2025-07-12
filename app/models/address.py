from mixins import TimestampMixin
from typing import Optional

class Address (TimestampMixin, table=True):
    __tablename__ = "addresses"

    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state: str
    zip: str