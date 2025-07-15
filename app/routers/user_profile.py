from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.utils.auth import get_current_user
from app.models.customer import Customer
from app.models.provider import Provider  # if you have this model

router = APIRouter(
    prefix="/users",
    tags=["user_profile"]
)

@router.get("/me")
async def read_current_user_profile(
        user_id: str = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    # Try customer
    # noinspection PyTypeChecker
    customer = session.exec(
        select(Customer).where(Customer.user_id == user_id)
    ).first()

    if customer:
        return {"role": "customer", "data": customer}

    # Try provider
    # noinspection PyTypeChecker
    provider = session.exec(
        select(Provider).where(Provider.user_id == user_id)
    ).first()

    if provider:
        return {"role": "provider", "data": provider}

    raise HTTPException(status_code=404, detail="User not found in customer or provider tables")