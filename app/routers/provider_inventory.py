# app/routers/provider_inventory.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.provider_inventory import (
    ProviderInventory,
    ProviderInventoryCreate,
    ProviderInventoryUpdate
)

router = APIRouter(
    prefix="/provider_inventory",
    tags=["provider_inventory"]
)

@router.post("/", response_model=ProviderInventory)
def create_provider_inventory(
        inventory_data: ProviderInventoryCreate,
        session: Session = Depends(get_session)
):
    provider_inventory = ProviderInventory(**inventory_data.dict())
    session.add(provider_inventory)
    session.commit()
    session.refresh(provider_inventory)
    return provider_inventory


@router.get("/", response_model=list[ProviderInventory])
def read_all_provider_inventory(session: Session = Depends(get_session)):
    return session.exec(select(ProviderInventory)).all()


@router.get("/{inventory_id}", response_model=ProviderInventory)
def read_provider_inventory(inventory_id: UUID, session: Session = Depends(get_session)):
    item = session.get(ProviderInventory, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Provider inventory not found")
    return item


@router.put("/{inventory_id}", response_model=ProviderInventory)
def update_provider_inventory(
        inventory_id: UUID,
        updates: ProviderInventoryUpdate,
        session: Session = Depends(get_session)
):
    item = session.get(ProviderInventory, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Provider inventory not found")
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{inventory_id}")
def delete_provider_inventory(inventory_id: UUID, session: Session = Depends(get_session)):
    item = session.get(ProviderInventory, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Provider inventory not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
