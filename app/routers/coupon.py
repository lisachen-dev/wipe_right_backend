from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.coupon import Coupon, CouponList
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import (
    create_one,
    delete_one,
    get_all,
    get_all_by_field,
    get_one,
    update_one,
)
from app.utils.user_helpers import get_user_scoped_record

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
