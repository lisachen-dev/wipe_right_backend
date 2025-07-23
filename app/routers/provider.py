from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.provider import Provider, ProviderCreate, ProviderUpdate
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import create_one, update_one, delete_one
from app.utils.user_helpers import get_user_scoped_record

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=Provider)
async def create_provider(
        payload: ProviderCreate,
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):

    db_provider = get_user_scoped_record(session, Provider, user_id)
    if db_provider:
        raise HTTPException(status_code=400, detail="Provider already exists")

    # Inject user_id into the data manually
    provider_data = payload.model_dump()
    provider_data["user_id"] = user_id

    return create_one(session, Provider, provider_data)

# AUTH: Return current user's provider record
@router.get("/me", response_model=Provider)
async def read_own_provider(
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):

    db_provider = get_user_scoped_record(session, Provider, user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_provider

# AUTH: Update current user's provider record
@router.patch("/me", response_model=Provider)
async def update_own_provider(
        update_data: ProviderUpdate,
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):

    db_provider = get_user_scoped_record(session, Provider, user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return update_one(session, Provider, db_provider.id, update_data.dict(exclude_unset=True))

# AUTH: Delete current user's provider record
@router.delete("/me", response_model=dict)
async def delete_own_provider(
        user_id: UUID = Depends(get_current_user_id),
        session: Session = Depends(get_session)
):
    db_provider=get_user_scoped_record(session, Provider, user_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return delete_one(session, Provider, db_provider.id)
