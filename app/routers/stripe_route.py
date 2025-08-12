import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import config
from app.db.session import get_session
from app.models.coupon import Coupon
from app.models.service import Service
from app.models.stripe_model import (
    PaymentIntentCreateRequest,
    PaymentIntentCreateResponse,
)
from app.utils.crud_helpers import get_one

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)

stripe.api_key = config.STRIPE_SECRET_KEY


# Payment Intent https://docs.stripe.com/api/payment_intents/create


@router.post("/create-payment-intent", response_model=PaymentIntentCreateResponse)
async def create_payment_request(
    data: PaymentIntentCreateRequest, session: Session = Depends(get_session)
):
    try:
        service: Service = get_one(session, Service, data.service_id)
        price = service.pricing

        if data.coupon_code:
            coupon = session.exec(
                select(Coupon).where(Coupon.coupon_code == data.coupon_code)
            ).first()

            if not coupon:
                raise HTTPException(status_code=400, detail="Invalid coupon")

            price = service.pricing * (1 - coupon.discount_value / 100)

        payment_intent = stripe.PaymentIntent.create(
            amount=int(price * 100), currency="usd"
        )
        return {"client_secret": payment_intent.client_secret}

    # payment error
    except stripe.CardError as e:
        raise HTTPException(status_code=402, detail=e.user_message)

    # invalid request error
    except stripe.InvalidRequestError:
        raise HTTPException(status_code=400, detail="Invalid request to Stripe")

    # bad gateway
    except stripe.error.StripeError:
        raise HTTPException(status_code=502, detail="Stripe service error.")

    # internal server error
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error.")
