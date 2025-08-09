from datetime import datetime, timedelta
from typing import List, Optional

from sqlmodel import Session

from app.models import Provider, Review, Service
from app.models.chat import ServiceRecommendation
from app.services.db_access import get_all_reviews_by_provider


def calculate_average_rating(reviews: List[Review]) -> float:
    if not reviews:
        return 0.0
    total = sum(review.rating for review in reviews)
    return round(total / len(reviews), 2)


def get_next_available_time(
    session: Session, service: Service, start_from: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate the next available time slot for a service.
    HACKATHON VERSION: Simple fixed times based on urgency.

    Args:
        session: Database session (not used in hackathon version)
        service: The service to check availability for
        start_from: Starting time to check from (not used in hackathon version)

    Returns:
        Next available datetime - 2 hours for emergencies, 24 hours for regular services
    """
    now = datetime.utcnow()

    # Check if this is an emergency service based on category/keywords
    emergency_keywords = [
        "emergency",
        "urgent",
        "plumbing",
        "electrical",
        "hvac",
        "repair",
    ]
    service_lower = (
        service.service_title + " " + (service.service_description or "")
    ).lower()

    is_emergency = any(keyword in service_lower for keyword in emergency_keywords)

    if is_emergency:
        # Emergency services: 2 hours from now
        available_time = now + timedelta(hours=2)
    else:
        # Regular services: 24 hours from now
        available_time = now + timedelta(hours=24)

    # Round to the nearest hour for cleaner times
    return available_time.replace(minute=0, second=0, microsecond=0)


def format_available_time(available_time: Optional[datetime]) -> str:
    """
    Format the available time in a user-friendly way.

    Args:
        available_time: The available datetime or None

    Returns:
        Formatted string like "Today at 2:00 PM" or "Tomorrow at 9:00 AM"
    """
    if not available_time:
        return "No availability found"

    now = datetime.utcnow()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    if available_time.date() == today:
        return f"Today at {available_time.strftime('%I:%M %p')}"
    elif available_time.date() == tomorrow:
        return f"Tomorrow at {available_time.strftime('%I:%M %p')}"
    else:
        return available_time.strftime("%A, %B %d at %I:%M %p")


def get_provider_display_name(provider: Provider) -> str:
    """
    Return company_name if available, otherwise "first last"
    """
    if provider.company_name:
        return provider.company_name
    return f"{provider.first_name} {provider.last_name}".strip()


def to_service_recommendation(
    service: Service, session: Session
) -> ServiceRecommendation:
    # Provider info
    provider_name = get_provider_display_name(service.provider)
    provider_reviews = get_all_reviews_by_provider(session, service.provider.id)

    # Get average rating for provider
    average_rating = calculate_average_rating(provider_reviews)

    # Get next available time
    next_available = get_next_available_time(session, service)

    return ServiceRecommendation(
        id=str(service.id),
        name=service.service_title,
        provider=provider_name,
        provider_id=str(service.provider_id),
        price=service.pricing,
        rating=average_rating,
        description=service.service_description or "",
        category=service.category or "",
        duration=service.duration,
        available_time=next_available,
    )


def map_services_to_recommendations(
    services: list[Service], session: Session
) -> list[ServiceRecommendation]:
    return [
        to_service_recommendation(service, session)
        for service in services
        if service.provider is not None
    ]
