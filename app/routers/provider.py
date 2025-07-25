from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from app.db.session import get_session
from app.models.provider import (
    Provider,
    ProviderCreate,
    ProviderUpdate,
    ProviderResponseDetail,
    ProviderPublicRead,
)
from app.models.reviews import Review, ReviewRead
from app.models.customer import Customer
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import create_one, update_one, delete_one, get_all, get_one
from app.utils.user_helpers import get_user_scoped_record

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Provider)
async def create_provider(
    payload: ProviderCreate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):

    db_provider = get_user_scoped_record(session, Provider, supabase_user_id)
    if db_provider:
        raise HTTPException(status_code=400, detail="Provider already exists")

    # Inject supabase_user_id into the data manually
    provider_data = payload.model_dump()
    provider_data["supabase_user_id"] = supabase_user_id

    return create_one(session, Provider, provider_data)


# Return all providers
@router.get("/all", response_model=list[ProviderPublicRead])
async def get_all_providers(session: Session = Depends(get_session)):
    return get_all(session, Provider)


# AUTH: Return current user's provider record
@router.get("/me", response_model=Provider)
async def read_own_provider(
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):

    db_provider = get_user_scoped_record(session, Provider, supabase_user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_provider


# Return provider details by ID
@router.get("/{provider_id}", response_model=ProviderResponseDetail)
async def get_provider_details(
    provider_id: UUID, session: Session = Depends(get_session)
):

    provider = get_one(session, Provider, provider_id)

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    recent_reviews = session.exec(
        select(
            Review.rating,
            Review.description,
            Review.created_at,
            Customer.first_name,
            Customer.last_name,
        )
        .join(Customer, Review.customer_id == Customer.id)
        .where(Review.provider_id == provider_id)
        .order_by(Review.created_at.desc())
        .limit(3)
    ).all()

    review_list = [
        ReviewRead(
            customer_name=f"{review.first_name} {review.last_name}",
            rating=review.rating,
            description=review.description,
            created_at=review.created_at,
        )
        for review in recent_reviews
    ]

    review_data = session.exec(
        select(
            func.count(Review.id).label("count"),
            func.avg(Review.rating).label("average"),
        ).where(Review.provider_id == provider_id)
    ).first()

    return ProviderResponseDetail(
        id=provider.id,
        phone_number=provider.phone_number,
        services=provider.services,
        reviews=review_list,
        review_count=review_data.count or 0,
        average_rating=float(review_data.average) if review_data.average else None
    )


# AUTH: Update current user's provider record
@router.patch("/me", response_model=Provider)
async def update_own_provider(
    update_data: ProviderUpdate,
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):

    db_provider = get_user_scoped_record(session, Provider, supabase_user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return update_one(
        session, Provider, db_provider.id, update_data.model_dump(exclude_unset=True)
    )


# AUTH: Delete current user's provider record
@router.delete("/me", response_model=dict)
async def delete_own_provider(
    supabase_user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    db_provider = get_user_scoped_record(session, Provider, supabase_user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return delete_one(session, Provider, db_provider.id)
