from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, text

# if TYPE_CHECKING:


class CouponBase(SQLModel):
    coupon_code: str = Field(unique=True)
    coupon_name: str
    discount_value: int


class Coupon(CouponBase, table=True):
    __tablename__ = "coupons"

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


class CouponList(SQLModel):
    coupon_code: str = Field(unique=True)
    coupon_name: str
    discount_value: int
