import httpx


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
    except Exception:
        return None, None

    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon

    return None, None
