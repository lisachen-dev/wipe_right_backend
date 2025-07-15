import os
import jwt
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="not-used")  # placeholder, not used with Supabase login (until Google auth)

# Use Supabase's JWT secret (from Project Settings > API Keys > service_role Legacy API Keys for now)
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")  # You must set this in your .env
JWT_ALGORITHM = "HS256"  # Supabase default

def decode_jwt(token: str) -> dict:
    try:
        decoded_payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> UUID:
    payload = decode_jwt(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return UUID(user_id)  # UUID used in Supabase `auth.users` table


# TEMPORARY: This fakes a logged-in user for Swagger testing
async def get_current_user() -> UUID:
    return UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")  # any static UUID that exists
