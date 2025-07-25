from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.booking import Booking, BookingCreate, BookingUpdate
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
