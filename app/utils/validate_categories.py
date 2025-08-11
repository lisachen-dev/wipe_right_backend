from fastapi import HTTPException

from app.models.service import ServiceEnum

SLUG_TO_ENUM_NAME: dict[str, str] = {
    "housecleaning": ServiceEnum.HOUSE_CLEANING.name,
    "lawnandgarden": ServiceEnum.LAWN_AND_GARDEN.name,
    "handymanandrepairs": ServiceEnum.HANDYMAN_AND_REPAIRS.name,
    "exteriorcleaning": ServiceEnum.EXTERIOR_CLEANING.name,
    "specializedcleaning": ServiceEnum.SPECIALIZED_CLEANING.name,
    "assemblyandinstallation": ServiceEnum.ASSEMBLY_AND_INSTALLATION.name,
}


def validate_category(category_name: str) -> str:
    """Validate a slug from the request and return the DB enum NAME.

    - Input: slug from the URL path (e.g. "housecleaning").
    - Output: the corresponding enum NAME (e.g. "HOUSE_CLEANING") to use in queries.
    - Raises: 400 with a friendly list of valid slugs if the input is unknown.

    We keep this strict (no fuzzy matching) so the accepted public API surface
    is explicit and predictable.
    """
    key = category_name.strip().lower()

    # Look up the enum name; if missing, report the allowed slugs.
    enum_name = SLUG_TO_ENUM_NAME.get(key)
    if not enum_name:
        valid = list(SLUG_TO_ENUM_NAME.keys())
        raise HTTPException(
            status_code=400,
            detail=f"invalid category, valid categories are: {valid}",
        )

    return enum_name
