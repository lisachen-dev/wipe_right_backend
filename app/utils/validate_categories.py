from fastapi import HTTPException
from app.models.service import ServiceEnum, Service


def validate_category(category_name: str):
    # creates an array of all the values in the Service Enum (right side of enum)
    valid_categories = [category.value for category in ServiceEnum]

    if category_name not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"invalid category, valid categories are: {valid_categories}",
        )
    try:
        # fetches the value from the enum based on the category name passed and was validated
        enum_name = None
        for category in ServiceEnum:
            if category.value == category_name:
                enum_name = category.name
                break
        return enum_name
    except:
        raise HTTPException(status_code=400, detail=f"{Service.__name__} not found")
