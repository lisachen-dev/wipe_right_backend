from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, text

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
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)


# [AUTH: CUSTOMER VIEW] GET ALL BOOKINGS
# TODO NEED TO CREATE SEPARATE CLASS FOR CUSTOMER VS PROVIDER
@router.get("/me", response_model=list[Booking])
async def read_bookings_by_customer(
    session: Session = Depends(get_session),
    supabase_user_id: UUID = Depends(get_current_user_id),
):
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)

    if not db_customer:
        raise HTTPException(status_code=404, details="Customer not found")

    return get_all_by_field(session, Booking, "customer_id", db_customer.id)


# [AUTH: PROVIDER VIEW] GET ALL BOOKINGS
# TODO NEED TO CREATE SEPARATE CLASS FOR CUSTOMER VS PROVIDER
@router.get("/provider/me", response_model=list[Booking])
async def read_bookings_by_provider(
    session: Session = Depends(get_session),
    supabase_user_id: UUID = Depends(get_current_user_id),
):
    db_provider = get_user_scoped_record(session, Provider, supabase_user_id)

    if not db_provider:
        raise HTTPException(status_code=404, details="Provider not found")

    return get_all_by_field(session, Booking, "provider_id", db_provider.id)


# [AUTH: CUSTOMER VIEW}GET ONE BOOKING
@router.get("/{booking_id}", response_model=Booking)
async def read_booking(booking_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, Booking, booking_id)


# GET one booking and its details
@router.get("/{booking_id}/details", response_model=BookingDetails)
async def read_bookings_details(
    booking_id: UUID, session: Session = Depends(get_session)
):
    try:
        # Use raw SQL to avoid relationship issues

        result = session.exec(
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
            .join(Address, Address.id == Booking.address_id)
            .where(Booking.id == booking_id)
        ).first()
        # query = text(
        #     """
        # SELECT
        #     b.id,
        #     b.start_time,
        #     b.status,
        #     c.phone_number as customer_phone_number,
        #     p.company_name,
        #     p.phone_number as provider_phone_number,
        #     a.street_address_1,
        #     a.street_address_2,
        #     a.city,
        #     a.state,
        #     a.zip
        # FROM bookings b
        # JOIN customers c ON c.id = b.customer_id
        # JOIN providers p ON p.id = b.provider_id
        # JOIN addresses a ON a.id = b.address_id
        # WHERE b.id = :booking_id
        # """
        # )

        # result = session.execute(query, {"booking_id": str(booking_id)}).first()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Booking not found",
            )

        return BookingDetails(
            id=result.id,
            start_time=result.start_time,
            status=result.status,
            provider_company_name=result.company_name,
            provider_phone_number=result.provider_phone_number,
            customer_phone_number=result.customer_phone_number,
            customer_address=CustomerAddressResponse(
                street_address_1=result.street_address_1,
                street_address_2=result.street_address_2,
                city=result.city,
                state=result.state,
                zip=result.zip,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_bookings_details: {e}")
        print(f"Booking ID: {booking_id}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# CREATE booking
# [AUTH: CUSTOMER VIEW] CREATE BOOKING
@router.post("/", response_model=Booking)
async def create_booking(
    booking: BookingCreate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    ### ------- Validate Stripe Payment Intent ID -------
    stripe_payment_id = booking.stripe_payment_id

    # verify request came through
    if not stripe_payment_id:
        raise HTTPException(status_code=400, detail="Missing payment intent ID")

    # validate existence on network
    try:
        payment_intent = stripe.PaymentIntent.retrieve(stripe_payment_id)
        print(f"=========PAYMENT_INTENT==============: {payment_intent.id}")
    except stripe.error.InvalidRequestError:
        raise HTTPException(status_code=400, detail="Invalid payment intent id")
    except stripe.error.StripeError:
        raise HTTPException(status_code=502, detail="Stripe service error")

    # confirm payment status success
    # https://docs.stripe.com/api/payment_intents/object#payment_intent_object-status
    if payment_intent.status != "succeeded":
        raise HTTPException(
            status_code=400,
            detail=f"Payment not confirmed. Status: {payment_intent.status}",
        )

    ### ------- Validate Authenticated Customer -------
    db_customer = get_user_scoped_record(session, Customer, supabase_user_id)

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    ### ------- Associate Address ID -------
    db_address = get_one(session, Address, booking.address_id)

    if db_address.customer_id != db_customer.id:
        raise HTTPException(
            status_code=403, detail="Address does not belong to this customer"
        )

    ### ------- Create Booking Data -------
    booking_data = booking.model_dump()
    booking_data["customer_id"] = db_customer.id

    return create_one(session, Booking, booking_data)


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
