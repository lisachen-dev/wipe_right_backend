from http.client import HTTPException
from uuid import UUID

import httpx
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from app import config

"""
params: auto_error
note: auto_error=True (default): FastAPI will reject missing/malformed headers before this runs
"""
auth_bearer_token = HTTPBearer()

class UnauthorizedMessage(BaseModel):
    detail: str = "Bearer token missing or invalid"

"""
Extend database timeouts to execute longer transactions
https://supabase.com/docs/guides/database/postgres/timeouts#session-level
"""
SUPABASE_HTTP_TIMEOUT=10

async def _supabase_get_user(token: str) -> Dict[str,Any]:
    # Validate Supabase access token by calling Supabase Auth.
    url = f"{config.SUPABASE_URL}/auth/v1/user"
    headers = {
        "apikey": config.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(timeout=SUPABASE_HTTP_TIMEOUT) as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=UnauthorizedMessage().detail
    )

async def get_current_user_id(
    auth_creds: Optional[HTTPAuthorizationCredentials] = Depends(auth_bearer_token)
) -> UUID:

    # Extract the bearer token (already validated by HTTPBearer) and return validated Supabase user in json
    user_data = await _supabase_get_user(auth_creds.credentials)
    try:
        return UUID(user_data["id"])
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or missing user ID from Supabase"
        )

async def get_supabase_user(
        auth_creds: Optional[HTTPAuthorizationCredentials] = Depends(auth_bearer_token)
):
    return await _supabase_get_user(auth_creds.credentials
)