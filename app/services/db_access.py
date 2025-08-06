from typing import List, cast
from uuid import UUID

from sqlmodel import Session

from app.models import Review, Service
from app.utils.crud_helpers import get_all, get_all_by_field


def get_all_reviews_by_provider(session: Session, provider_id: UUID) -> List[Review]:
    return cast(
        List[Review], get_all_by_field(session, Review, "provider_id", provider_id)
    )


def get_all_services(session: Session = List[Service]):
    return get_all(session, Service)
