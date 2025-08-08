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
from app.utils.geocoding import geocode_address
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
async def create_address(
    address: AddressCreate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    full_address = (
        f"{address.street_address_1}, {address.city}, {address.state} {address.zip}"
    )
    lat, lon = await geocode_address(full_address)

    data = address.model_dump()
    data["customer_id"] = db_customer.id
    data["latitude"] = lat
    data["longitude"] = lon

    return create_one(session, Address, data)


# UPDATE
@router.patch("/{address_id}", response_model=Address)
async def update_address(
    address_id: UUID,
    update_data: AddressUpdate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    address = get_one(session, Address, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if address.customer_id != db_customer.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_street_1 = update_data.street_address_1 or address.street_address_1
    new_street_2 = update_data.street_address_2 or address.street_address_2
    new_city = update_data.city or address.city
    new_state = update_data.state or address.state
    new_zip = update_data.zip or address.zip

    full_address = f"{new_street_1}, {new_city}, {new_state} {new_zip}"

    lat, lon = await geocode_address(full_address)

    data = AddressUpdate(
        street_address_1=new_street_1,
        street_address_2=new_street_2,
        city=new_city,
        state=new_state,
        zip=new_zip,
        latitude=lat,
        longitude=lon,
    )

    return update_one(session, Address, address_id, data.model_dump())


@router.delete("/{address_id}", response_model=dict)
def delete_address(address_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, Address, address_id)
