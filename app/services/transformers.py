from typing import List

from sqlmodel import Session

from app.models import Provider, Review, Service
from app.models.chat import ServiceRecommendation
from app.services.db_access import get_all_reviews_by_provider


def calculate_average_rating(reviews: List[Review]) -> float:
    if not reviews:
        return 0.0
    total = sum(review.rating for review in reviews)
    return round(total / len(reviews), 2)


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

    return ServiceRecommendation(
        id=str(service.id),
        name=service.service_title,
        provider=provider_name,
        price=service.pricing,
        rating=average_rating,
        description=service.service_description or "",
        category=service.category or "",
        duration=service.duration,
    )


def map_services_to_recommendations(
    services: list[Service], session: Session
) -> list[ServiceRecommendation]:
    return [
        to_service_recommendation(service, session)
        for service in services
        if service.provider is not None
    ]
