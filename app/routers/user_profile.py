from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.utils.auth import get_current_user_id
from app.models.customer import Customer
from app.models.provider import Provider

router = APIRouter(
    prefix="/users",
    tags=["user_profile"]
)

@router.get("/me")
async def read_current_user_profile(
        user_id: str = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):
    # Try customer
    customer_statement = select(Customer).where(Customer.auth_user_id == user_id)
    db_customer: Customer | None = session.scalar(customer_statement)

    if db_customer:
        return {"role": "customer", "data": db_customer}

    # Try provider
    provider_statement = select(Provider).where(Provider.user_id == user_id)
    db_provider: Provider | None = session.scalar(provider_statement)

    if db_provider:
        return {"role": "provider", "data": db_provider}

    raise HTTPException(status_code=404, detail="User not found in customer or provider tables")