from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.address import Address
from app.models.booking import (
    Booking,
    BookingCreate,
    BookingDetails,
    BookingUpdate,
    CustomerAddressResponse,
)
from app.models.customer import Customer
from app.models.provider import Provider
from app.utils.crud_helpers import (
    create_one,
    delete_one,
    get_all,
    get_one,
    update_one,
)

router = APIRouter(
    prefix="/bookings", tags=["bookings"], responses={404: {"description": "Not found"}}
)


# GET all bookings
@router.get("/", response_model=list[Booking])
async def read_bookings(session: Session = Depends(get_session)):
    return get_all(session, Booking)


# GET one booking
@router.get("/{booking_id}", response_model=Booking)
async def read_booking(booking_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, Booking, booking_id)


# GET one booking and its details
@router.get("/{booking_id}/details", response_model=BookingDetails)
async def read_bookings_details(
    booking_id: UUID, session: Session = Depends(get_session)
):
    try:
        found_booking = session.exec(
            select(
                Booking.id,
                Booking.start_time,
                Booking.status,
                Customer.phone_number.label("customer_phone_number"),
                Provider.company_name,
                Provider.phone_number.label("provider_phone_number"),
                Address.street_address_1,
                Address.street_address_2,
                Address.city,
                Address.state,
                Address.zip,
            )
            .join(Customer, Customer.id == Booking.customer_id)
            .join(Provider, Provider.id == Booking.provider_id)
            .join(Address, Address.customer_id == Booking.customer_id)
            .where(Booking.id == booking_id)
        ).first()
        if not found_booking:
            raise HTTPException(
                status_code=400,
                detail="invalid booking id sent try again",
            )

        return BookingDetails(
            id=found_booking.id,
            start_time=found_booking.start_time,
            status=found_booking.status,
            provider_company_name=found_booking.company_name,
            provider_phone_number=found_booking.provider_phone_number,
            customer_phone_number=found_booking.customer_phone_number,
            customer_address=CustomerAddressResponse(
                street_address_1=found_booking.street_address_1,
                street_address_2=found_booking.street_address_2,
                city=found_booking.city,
                state=found_booking.state,
                zip=found_booking.zip,
            ),
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


# CREATE booking
@router.post("/", response_model=Booking)
async def create_booking(
    booking: BookingCreate, session: Session = Depends(get_session)
):
    return create_one(session, Booking, booking.dict())


# UPDATE booking
@router.patch("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: UUID,
    update_data: BookingUpdate,
    session: Session = Depends(get_session),
):
    return update_one(
        session, Booking, booking_id, update_data.dict(exclude_unset=True)
    )


# DELETE booking
@router.delete("/{booking_id}", response_model=dict)
async def delete_booking(booking_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, Booking, booking_id)
