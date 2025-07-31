from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.booking import (
    Booking,
    BookingBase,
    BookingCreate,
    BookingStatusUpdate,
    BookingUpdate,
)
from app.models.provider import Provider
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import (
    create_one,
    delete_one,
    get_all,
    get_one,
    update_one,
)
from app.utils.user_helpers import get_user_scoped_record

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


@router.patch("/{booking_id}/status", response_model=BookingBase)
async def update_booking_status(
    booking_id: UUID,
    update_data: BookingStatusUpdate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_provider = get_user_scoped_record(session, Provider, supabase_user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    booking = get_one(session, Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.provider_id != db_provider.id:
        raise HTTPException(
            status_code=403, detail="Booking does not belong to this Provider"
        )

    return update_one(
        session, Booking, booking_id, update_data.model_dump(exclude_unset=True)
    )


# DELETE booking
@router.delete("/{booking_id}", response_model=dict)
async def delete_booking(booking_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, Booking, booking_id)
