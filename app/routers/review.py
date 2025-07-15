from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.models.reviews import Review, ReviewCreate, ReviewUpdate
from app.db.session import get_session
from app.utils.crud_helpers import get_all, get_one, create_one, update_one, delete_one

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    responses={404: {"description": "Not found"}}
)

# PUBLIC: Get all reviews
@router.get("/", response_model=list[Review])
async def read_reviews(session: Session = Depends(get_session)):
    return get_all(session, Review)

# PUBLIC: Get a single review
@router.get("/{review_id}", response_model=Review)
async def read_review(review_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, Review, review_id)

# AUTH: Create a review (for now, auth optional)
@router.post("/", response_model=Review)
async def create_review(
        review: ReviewCreate,
        session: Session = Depends(get_session)
):
    return create_one(session, Review, review.dict())

# AUTH: Update a review (for now, no owner check)
@router.patch("/{review_id}", response_model=Review)
async def update_review(
        review_id: UUID,
        update_data: ReviewUpdate,
        session: Session = Depends(get_session)
):
    return update_one(session, Review, review_id, update_data.dict(exclude_unset=True))

# AUTH: Delete a review
@router.delete("/{review_id}", response_model=dict)
async def delete_review(
        review_id: UUID,
        session: Session = Depends(get_session)
):
    return delete_one(session, Review, review_id)
