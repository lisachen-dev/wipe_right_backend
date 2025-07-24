from uuid import UUID
from typing import Optional, Type
from sqlmodel import SQLModel, Session, select


def get_user_scoped_record(
        session: Session,
        model_class: Type[SQLModel],
        supabase_user_id: UUID,
) -> Optional[SQLModel]:
    statement = select(model_class).where(model_class.supabase_user_id == supabase_user_id)
    db_obj: model_class | None = session.scalar(statement)

    return db_obj