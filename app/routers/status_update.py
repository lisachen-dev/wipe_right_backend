from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.status_update import (
    StatusUpdate,
    StatusUpdateCreate,
    StatusUpdateUpdate,
)
from app.utils.crud_helpers import create_one, delete_one, get_all, get_one, update_one

router = APIRouter(
    prefix="/status_updates",
    tags=["status_updates"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[StatusUpdate])
async def read_all_status_updates(session: Session = Depends(get_session)):
    return get_all(session, StatusUpdate)


@router.get("/{record_id}", response_model=StatusUpdate)
async def read_status_update(record_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, StatusUpdate, record_id)


@router.post("/", response_model=StatusUpdate)
async def create_status_update(
    data: StatusUpdateCreate, session: Session = Depends(get_session)
):
    return create_one(session, StatusUpdate, data.dict())


@router.patch("/{record_id}", response_model=StatusUpdate)
async def update_status_update(
    record_id: UUID,
    update_data: StatusUpdateUpdate,
    session: Session = Depends(get_session),
):
    return update_one(
        session, StatusUpdate, record_id, update_data.dict(exclude_unset=True)
    )


@router.delete("/{record_id}", response_model=dict)
async def delete_status_update(
    record_id: UUID, session: Session = Depends(get_session)
):
    return delete_one(session, StatusUpdate, record_id)
