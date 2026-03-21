from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/rooms")
async def get_blackjack_rooms(current_user: User = Depends(get_current_user)):
    """Get list of active Blackjack rooms"""
    return {"rooms": []}
