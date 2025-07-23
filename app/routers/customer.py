from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.models.customer import Customer, CustomerCreate, CustomerUpdate
from app.db.session import get_session
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import create_one, update_one, delete_one
from app.utils.user_helpers import get_user_scoped_record

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=Customer)
async def create_customer(
        payload: CustomerCreate,
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):

    db_customer = get_user_scoped_record(session, Customer, user_id)
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer already exists")

    # Inject user_id into the data manually
    data = payload.model_dump()
    data["user_id"] = user_id

    return create_one(session, Customer, data)

# AUTH: Return current user's customer record
@router.get("/me", response_model=Customer)
async def read_own_customer(
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):

    db_customer = get_user_scoped_record(session, Customer, user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# AUTH: Update current user's customer record
@router.patch("/me", response_model=Customer)
async def update_own_customer(
        update_data: CustomerUpdate,
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):

    db_customer = get_user_scoped_record(session, Customer, user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return update_one(session, Customer, db_customer.id, update_data.model_dump(exclude_unset=True))

# AUTH: Delete current user's customer record
@router.delete("/me", response_model=dict)
async def delete_own_customer(
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):
    db_customer = get_user_scoped_record(session, Customer, user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return delete_one(session, Customer, db_customer.id)
