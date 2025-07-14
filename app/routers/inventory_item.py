import uuid
from fastapi import HTTPException

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.models.inventory_item import InventoryItemsBase, InventoryItemCreate, InventoryItemUpdate
from app.db.session import get_session
from app.utils.crud_helpers import get_all, get_one, create_one, update_one, delete_one

router = APIRouter(
    prefix="/inventory_items",
    tags=["inventory_items"],
    responses={404: {"description": "Not found"}}
)

# GET ALL
@router.get("/", response_model=list[InventoryItemsBase])
async def read_inventory_items(session: Session = Depends(get_session)):
    return get_all(session, InventoryItemsBase)

# GET ONE
@router.get("/{inventory_item_id}", response_model=InventoryItemsBase)
async def read_inventory_item(inventory_item_id: uuid.UUID, session: Session = Depends(get_session)):
    return get_one(session, InventoryItemsBase, inventory_item_id)

# CREATE
@router.post("/", response_model=InventoryItemsBase)
async def create_inventory_item(inventory_item: InventoryItemCreate, session: Session = Depends(get_session)):
    return create_one(session, InventoryItemsBase, inventory_item.dict())

# UPDATE
@router.patch("/{inventory_item_id}", response_model=InventoryItemsBase)
async def update_inventory_item(
        inventory_item_id: uuid.UUID,
        update_data: InventoryItemUpdate,
        session: Session = Depends(get_session)):
    return update_one(session, InventoryItemsBase, inventory_item_id, update_data.dict(exclude_unset=True))

# DELETE
@router.delete("/{inventory_item_id}", response_model=InventoryItemsBase)
async def delete_inventory_item(
        inventory_item_id: uuid.UUID,
        session: Session = Depends(get_session)):
    return delete_one(session, InventoryItemsBase, inventory_item_id)


