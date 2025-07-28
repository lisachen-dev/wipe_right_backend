from fastapi import HTTPException
from app.models.service import ServiceEnum


def validate_category(category_name: str):
    valid_categories = [category.value for category in ServiceEnum]

    if category_name not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"invalid category, valid categories are: {valid_categories}",
        )

    # if it gets here, there will always be a match
    for category in ServiceEnum:
        if category.value == category_name:
            return category.name

    # Explicit fallback if somehow no match is found
    raise HTTPException(
        status_code=500, detail="Unexpected error in category validation"
    )
