import logging

import httpx
from async_lru import alru_cache
from fastapi import HTTPException

logger = logging.getLogger(__name__)


@alru_cache(maxsize=1000)  # Cache results in memory
async def geocode_address(address_string: str) -> tuple[float | None, float | None]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address_string, "format": "json", "limit": 1}
    headers = {
        "User-Agent": "ServiceBookingApp/1.0 (contact: teammadeyoulook2025@gmail.com)"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.RequestError as e:
        logger.error(f"Geocoding request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Geocoding response error: {e}")

    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon

    return None, None
