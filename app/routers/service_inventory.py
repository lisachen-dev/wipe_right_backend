from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.service_inventory import ServiceInventory, ServiceInventoryCreate, ServiceInventoryUpdate
from app.db.session import get_session
from app.utils.crud_helpers import get_all, get_one, create_one, update_one, delete_one

router = APIRouter(
    prefix="/service_inventory",
    tags=["service_inventory"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[ServiceInventory])
async def read_service_inventory(session: Session = Depends(get_session)):
    return get_all(session, ServiceInventory)

@router.get("/{record_id}", response_model=ServiceInventory)
async def read_service_inventory_record(record_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, ServiceInventory, record_id)

@router.post("/", response_model=ServiceInventory)
async def create_service_inventory(data: ServiceInventoryCreate, session: Session = Depends(get_session)):
    return create_one(session, ServiceInventory, data.dict())

@router.patch("/{record_id}", response_model=ServiceInventory)
async def update_service_inventory(record_id: UUID, update_data: ServiceInventoryUpdate, session: Session = Depends(get_session)):
    return update_one(session, ServiceInventory, record_id, update_data.dict(exclude_unset=True))

@router.delete("/{record_id}", response_model=dict)
async def delete_service_inventory(record_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, ServiceInventory, record_id)
