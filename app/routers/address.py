from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.address import Address, AddressCreate, AddressUpdate
from app.db.session import get_session
from app.utils.crud_helpers import get_all, get_one, create_one, update_one, delete_one

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[Address])
def read_addresses(session: Session = Depends(get_session)):
    return get_all(session, Address)

@router.get("/{address_id}", response_model=Address)
def read_address(address_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, Address, address_id)

@router.post("/", response_model=Address)
def create_address(address: AddressCreate, session: Session = Depends(get_session)):
    return create_one(session, Address, address.dict())

@router.patch("/{address_id}", response_model=Address)
def update_address(address_id: UUID, update_data: AddressUpdate, session: Session = Depends(get_session)):
    return update_one(session, Address, address_id, update_data.dict(exclude_unset=True))

@router.delete("/{address_id}", response_model=dict)
def delete_address(address_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, Address, address_id)
