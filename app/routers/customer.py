from uuid import UUID
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.customer import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
    CustomersBookings,
)
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import create_one, delete_one, update_one, get_all
from app.utils.user_helpers import get_user_scoped_record
from app.models.booking import Booking
from app.models.enums import StatusEnum
from app.models.provider import Provider
from app.models.service import Service

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Customer)
async def create_customer(
    payload: CustomerCreate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer already exists")

    # Inject supabase_user_id into the data manually
    data = payload.model_dump()
    data["supabase_user_id"] = supabase_user_id

    return create_one(session, Customer, data)


# AUTH: Return current user's customer record
@router.get("/me", response_model=Customer)
async def read_own_customer(
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


# Used to test customer relationships
@router.get("/all", response_model=list[Customer])
async def read_all_customers(session: Session = Depends(get_session)):
    return get_all(session, Customer)


# GET all upcoming bookings and need review bookings for current customer
@router.get("/{customer_id}/dashboard", response_model=CustomersBookings)
async def read_users_bookings(
    customer_id: UUID, session: Session = Depends(get_session)
):
    if not customer_id:
        raise HTTPException(status_code=400, detail="user id not found")

    # Get bookings for the specific customer
    bookings = session.exec(
        select(
            Booking.start_time,
            Booking.status,
            Provider.company_name,
            Provider.first_name,
            Provider.last_name,
            Service.service_title,
        )
        .join(Provider, Provider.id == Booking.provider_id)
        .join(Service, Service.id == Booking.service_id)
        .where(Booking.customer_id == customer_id)
    ).all()

    completed_needs_review = []
    upcoming_bookings = []
    for booking in bookings:
        booking_dict = dict(booking._asdict())
        if booking.status == StatusEnum.review_needed:
            completed_needs_review.append(
                {
                    **booking_dict,
                    "provider_first_name": booking_dict["first_name"],
                    "provider_last_name": booking_dict["last_name"],
                    "provider_company_name": booking_dict["company_name"],
                }
            )
        elif (
            booking.status != StatusEnum.cancelled
            or booking.status != StatusEnum.completed
        ):
            upcoming_bookings.append(
                {
                    **booking_dict,
                    "provider_first_name": booking_dict["first_name"],
                    "provider_last_name": booking_dict["last_name"],
                    "provider_company_name": booking_dict["company_name"],
                }
            )

    return CustomersBookings(
        completed_needs_review=completed_needs_review,
        upcoming_bookings=upcoming_bookings,
    )


# AUTH: Update current user's customer record
@router.patch("/me", response_model=Customer)
async def update_own_customer(
    update_data: CustomerUpdate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Type cast since we know it's a Customer instance
    customer = cast(Customer, db_customer)
    return update_one(
        session, Customer, customer.id, update_data.model_dump(exclude_unset=True)
    )


# AUTH: Delete current user's customer record
@router.delete("/me", response_model=dict)
async def delete_own_customer(
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Type cast since we know it's a Customer instance
    customer = cast(Customer, db_customer)
    return delete_one(session, Customer, customer.id)
