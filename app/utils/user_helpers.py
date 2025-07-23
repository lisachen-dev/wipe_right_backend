from uuid import UUID
from typing import Optional, Type
from sqlmodel import SQLModel, Session, select


def get_user_scoped_record(
        session: Session,
        model_class: Type[SQLModel],
        user_id: UUID,
) -> Optional[SQLModel]:
    statement = select(model_class).where(model_class.user_id == user_id)
    db_obj: model_class | None = session.scalar(statement)

    return db_obj