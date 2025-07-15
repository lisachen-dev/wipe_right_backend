from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.db.session import get_session
from app.utils.crud_helpers import get_all, get_one, create_one, update_one, delete_one

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[Transaction])
async def read_all_transactions(session: Session = Depends(get_session)):
    return get_all(session, Transaction)

@router.get("/{record_id}", response_model=Transaction)
async def read_transaction(record_id: UUID, session: Session = Depends(get_session)):
    return get_one(session, Transaction, record_id)

@router.post("/", response_model=Transaction)
async def create_transaction(data: TransactionCreate, session: Session = Depends(get_session)):
    return create_one(session, Transaction, data.dict())

@router.patch("/{record_id}", response_model=Transaction)
async def update_transaction(record_id: UUID, update_data: TransactionUpdate, session: Session = Depends(get_session)):
    return update_one(session, Transaction, record_id, update_data.dict(exclude_unset=True))

@router.delete("/{record_id}", response_model=dict)
async def delete_transaction(record_id: UUID, session: Session = Depends(get_session)):
    return delete_one(session, Transaction, record_id)
