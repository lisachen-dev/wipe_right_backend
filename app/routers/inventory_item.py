import uuid
from fastapi import HTTPException

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.models.inventory_item import InventoryItemsBase, InventoryItemCreate, InventoryItemUpdate
from app.db.session import get_session


router = APIRouter(
    prefix="/inventory_items",
    tags=["inventory_items"],
    responses={404: {"description": "Not found"}}
)

# GET ALL
@router.get("/", response_model=list[InventoryItemsBase])
async def read_inventory_items(session: Session = Depends(get_session)):
    inventory_items = session.exec(select(InventoryItemsBase)).all()
    return inventory_items

# GET ONE
@router.get("/{inventory_item_id}")
async def read_inventory_item(inventory_item_id: uuid.UUID, session: Session = Depends(get_session)):
    inventory_item = session.get(InventoryItemsBase, inventory_item_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return inventory_item

# CREATE
@router.post("/", response_model=InventoryItemsBase)
async def create_inventory_item(inventory_item: InventoryItemCreate, session: Session = Depends(get_session)):

    # Get the data the user sends
    new_item = InventoryItemsBase(
        item_name = inventory_item.item_name,
        description = inventory_item.description,
        unit = inventory_item.unit,
        cost = inventory_item.cost
    )

    # Commit the changes and refresh the data
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item

# UPDATE
@router.patch("/{inventory_item_id}", response_model=InventoryItemsBase)
async def update_inventory_item(
        inventory_item_id: uuid.UUID,
        item_update: InventoryItemUpdate,
        session: Session = Depends(get_session)):

    # Fetch item
    stored_inventory_item = session.get(InventoryItemsBase, inventory_item_id)
    if not stored_inventory_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Fetch user defined fields
    update_data = item_update.dict(exclude_unset=True)

    # Apply the updates
    for field, value in update_data.items():
        setattr(stored_inventory_item, field, value)

    # Commit changes and refresh data
    session.add(stored_inventory_item)
    session.commit()
    session.refresh(stored_inventory_item)
    return stored_inventory_item

# DELETE
@router.delete("/{inventory_item_id}", response_model=InventoryItemsBase)
async def delete_inventory_item(
        inventory_item_id: uuid.UUID,
        session: Session = Depends(get_session)):

    # Fetch item
    stored_inventory_item = session.get(InventoryItemsBase, inventory_item_id)
    if not stored_inventory_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Delete and commit
    session.delete(stored_inventory_item)
    session.commit()

    # Item deleted, nothing to return
    return None