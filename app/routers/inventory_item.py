from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.inventory_item import (
    InventoryItemCreate,
    InventoryItems,
    InventoryItemUpdate,
)
from app.utils.crud_helpers import create_one, delete_one, get_all, get_one, update_one

router = APIRouter(
    prefix="/inventory_items",
    tags=["inventory_items"],
    responses={404: {"description": "Not found"}},
)


# GET ALL
@router.get("/", response_model=list[InventoryItems])
async def read_inventory_items(session: Session = Depends(get_session)):
    return get_all(session, InventoryItems)


# GET ONE
@router.get("/{inventory_item_id}", response_model=InventoryItems)
async def read_inventory_item(
    inventory_item_id: UUID, session: Session = Depends(get_session)
):
    return get_one(session, InventoryItems, inventory_item_id)


# CREATE
@router.post("/", response_model=InventoryItems)
async def create_inventory_item(
    inventory_item: InventoryItemCreate, session: Session = Depends(get_session)
):
    return create_one(session, InventoryItems, inventory_item.dict())


# UPDATE
@router.patch("/{inventory_item_id}", response_model=InventoryItems)
async def update_inventory_item(
    inventory_item_id: UUID,
    update_data: InventoryItemUpdate,
    session: Session = Depends(get_session),
):
    return update_one(
        session, InventoryItems, inventory_item_id, update_data.dict(exclude_unset=True)
    )


# DELETE
@router.delete("/{inventory_item_id}", response_model=InventoryItems)
async def delete_inventory_item(
    inventory_item_id: UUID, session: Session = Depends(get_session)
):
    return delete_one(session, InventoryItems, inventory_item_id)
