from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.auth import get_current_user
from datetime import datetime
import random

router = APIRouter()

@router.post("/start")
async def start_memory_game(current_user: User = Depends(get_current_user)):
    """Start a memory card game"""
    emojis = ["🎮", "🎯", "🎨", "🎭", "🎪", "🎫", "🎬", "🎤"]
    cards = emojis * 2
    random.shuffle(cards)
    game_id = f"memory_{current_user.id}_{datetime.utcnow().timestamp()}"
    return {
        "game_id": game_id,
        "cards": cards,
        "moves": 0,
        "matches": 0,
        "start_time": datetime.utcnow().isoformat()
    }

@router.post("/flip")
async def flip_memory_card(
    game_id: str,
    card_index: int,
    current_user: User = Depends(get_current_user)
):
    """Flip a card in memory game (Simulated for now)"""
    return {
        "card_index": card_index,
        "card_value": "🎮",
        "is_match": False,
        "moves": 1,
        "matches": 0,
        "game_complete": False
    }
