import uuid

from fastapi import HTTPException
from sqlmodel import Session, select


# GET ALL
def get_all(session: Session, model):
    return session.exec(select(model)).all()


# GET ONE
def get_one(session: Session, model, obj_id: uuid.UUID):
    obj = session.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


# CREATE
def create_one(session: Session, model, data: dict):

    # Get the data the user sends
    obj = model(**data)

    # Commit the changes and refresh the data
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


# UPDATE
def update_one(session: Session, model, obj_id: uuid.UUID, update_data: dict):
    # Fetch obj
    stored_obj = get_one(session, model, obj_id)

    # Apply the updates
    for field, value in update_data.items():
        setattr(stored_obj, field, value)

    # Commit changes and refresh data
    session.add(stored_obj)
    session.commit()
    session.refresh(stored_obj)
    return stored_obj


# DELETE
def delete_one(session: Session, model, obj_id: uuid.UUID):
    # Fetch obj
    stored_obj = get_one(session, model, obj_id)

    # Delete and commit
    session.delete(stored_obj)
    session.commit()

    # Item deleted, return confirmation
    return {"detail": f"{model.__name__} deleted successfully"}
