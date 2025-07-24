from fastapi import APIRouter, Depends
from app.utils.auth import get_supabase_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.get("/me")
async def get_supabase_profile(
    user = Depends(get_supabase_user)
):
    return user