from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.address import Address, AddressCreate, AddressUpdate
from app.models.customer import Customer
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import (
    create_one,
    delete_one,
    get_all_by_field,
    get_one,
    update_one,
)
from app.utils.user_helpers import get_user_scoped_record

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
    responses={404: {"description": "Not found"}},
)


# [AUTH: CUSTOMER VIEW] GET ALL ADDRESSES
@router.get("/me", response_model=list[Address])
def read_addresses(
    session: Session = Depends(get_session),
    supabase_user_id: UUID = Depends(get_current_user_id),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return get_all_by_field(session, Address, "customer_id", db_customer.id)


# GET ONE
@router.get("/{address_id}", response_model=Address)
def read_address(address_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, Address, address_id)


# CREATE
@router.post("/", response_model=Address)
def create_address(address: AddressCreate, session: Session = Depends(get_session)):
    return create_one(session, Address, address.dict())


# UPDATE
@router.patch("/{address_id}", response_model=Address)
def update_address(
    address_id: UUID,
    update_data: AddressUpdate,
    session: Session = Depends(get_session),
):
    return update_one(
        session, Address, address_id, update_data.dict(exclude_unset=True)
    )


@router.delete("/{address_id}", response_model=dict)
def delete_address(address_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, Address, address_id)
