from requests.sessions import Session

from app.models import Service
from app.utils.crud_helpers import get_all


def get_all_services(session: Session = list[Service]):
    return get_all(session, Service)
