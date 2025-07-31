from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.booking import Booking, BookingCreate, BookingUpdate, BookingDetails
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
    # selects the details from the booking
    # now i need the details of customers address
    # next is providers detials company name and phone number
    found_booking = session.exec(
        select(Booking.id, Booking.start_time, Booking.status).where(
            Booking.id == booking_id
        )
    ).first()
    try:
        if not found_booking:
            raise HTTPException(
                status_code=400,
                detail="invalid booking id sent try again",
            )

        print("found booking", found_booking)
        return BookingDetails(
            id=found_booking.id,
            start_time=found_booking.start_time,
            status=found_booking.status,
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
