from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import random

router = APIRouter()

class TypingTestRequest(BaseModel):
    text: str
    typed_text: str
    time_taken: float

TYPING_TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice makes perfect when learning to type faster and more accurately.",
    "Technology has revolutionized the way we communicate and work together.",
    "In the digital age, typing skills are essential for productivity and efficiency.",
    "Learning to type without looking at the keyboard requires patience and dedication.",
    "The journey of a thousand miles begins with a single step forward.",
    "Success is not final, failure is not fatal, it is the courage to continue that counts.",
    "Innovation distinguishes between a leader and a follower in any field.",
    "The only way to do great work is to love what you do every single day.",
    "Excellence is never an accident, it is always the result of high intention."
]

def get_typing_rating(wpm: float, accuracy: float) -> str:
    if accuracy >= 95 and wpm >= 80: return "Exceptional"
    if accuracy >= 90 and wpm >= 60: return "Excellent"
    if accuracy >= 85 and wpm >= 45: return "Good"
    if accuracy >= 80 and wpm >= 35: return "Average"
    return "Needs Practice"

@router.post("/start")
async def start_typing_test(current_user: User = Depends(get_current_user)):
    text = random.choice(TYPING_TEXTS)
    game_id = f"typing_{current_user.id}_{datetime.utcnow().timestamp()}"
    return {
        "game_id": game_id,
        "text": text,
        "start_time": datetime.utcnow().isoformat()
    }

@router.post("/submit")
async def submit_typing_test(
    request: TypingTestRequest,
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    text = request.text
    typed_text = request.typed_text
    time_taken = request.time_taken
    
    correct_chars = sum(1 for i, char in enumerate(typed_text) if i < len(text) and char == text[i])
    accuracy = (correct_chars / len(text)) * 100 if text else 0
    
    characters_typed = len(typed_text)
    minutes_taken = time_taken / 60
    wpm = (characters_typed / 5) / minutes_taken if minutes_taken > 0 else 0
    
    base_score = int(wpm * 10 + accuracy)
    time_bonus = max(0, 100 - int(time_taken))
    total_score = base_score + time_bonus
    
    kpi_reward = 0
    if accuracy >= 95 and wpm >= 60: kpi_reward = 30
    elif accuracy >= 90 and wpm >= 40: kpi_reward = 20
    elif accuracy >= 80 and wpm >= 30: kpi_reward = 10
    
    if kpi_reward > 0:
        current_user.kpi_current += kpi_reward
        current_user.save()
        KPIHistory(
            user=current_user,
            amount=kpi_reward,
            balance_after=current_user.kpi_current,
            source="typing_test",
            reason=f"Typing test: {wpm:.1f} WPM, {accuracy:.1f}% accuracy"
        ).save()
    
    return {
        "wpm": round(wpm, 1),
        "accuracy": round(accuracy, 1),
        "time_taken": time_taken,
        "total_score": total_score,
        "kpi_reward": kpi_reward,
        "performance_rating": get_typing_rating(wpm, accuracy),
        "new_balance": current_user.kpi_current
    }
