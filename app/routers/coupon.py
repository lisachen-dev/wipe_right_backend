from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.coupon import Coupon, CouponList
from app.utils.crud_helpers import (
    get_all,
)

router = APIRouter(
    prefix="/coupons",
    tags=["coupon"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[CouponList])
def read_all_coupons(session: Session = Depends(get_session)):
    return get_all(
        session,
        Coupon,
    )
