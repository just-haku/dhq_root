from pydantic import BaseModel
from fastapi import APIRouter, Depends
from app.models.user import User
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user

router = APIRouter()

class GameScore(BaseModel):
    game_type: str
    score: int
    metadata: dict = {}

from app.models.arcade import UserArcadeProfile

@router.post("/scores/submit")
async def submit_game_score(
    score: GameScore,
    current_user: User = Depends(get_current_user)
):
    """Submit a game score and award KPI rewards or update chips"""
    reward_kpi = 0
    reward_chips = 0
    reason = f"Game score in {score.game_type}"
    
    # Get Arcade Profile
    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user).save()
    
    difficulty = score.metadata.get("difficulty", "MEDIUM").upper()
    
    if score.game_type in ["blackjack", "bigtwo"]:
        # Gambling games use chips
        reward_chips = score.score # score is chip delta
        profile.add_chips(reward_chips)
        reason = f"{score.game_type.capitalize()} {'win' if reward_chips > 0 else 'loss' if reward_chips < 0 else 'push'}"
    else:
        # Regular games use scaled KPI
        base_rewards = {
            "wordle": 50,
            "2048": 80,
            "wordsearch": 40,
            "tictactoe": 20,
            "bovo": 100,
            "doodlejump": 70,
            "flappybird": 90,
            "typing": 30,
            "memory": 25
        }
        
        multiplier = {"EASY": 0.5, "MEDIUM": 1.0, "HARD": 2.5, "EXTREME": 5.0}
        mult = multiplier.get(difficulty, 1.0)
        
        base = base_rewards.get(score.game_type, 10)
        
        if score.game_type == "2048":
            reward_kpi = int((score.score // 1000) * mult)
        elif score.game_type == "wordle":
            # Wordle win gives full scaled; completion (non-win) gives 5 KPI (fixed)
            if score.score > 0:
                reward_kpi = int(base * mult)
            else:
                reward_kpi = 5 # Completion bonus
        else:
            reward_kpi = int(base * mult) if score.score > 0 else 0
            
        # Add KPI via centralized profile method
        if reward_kpi > 0:
            profile.add_kpi(reward_kpi, 'GAME', description=reason)

    return {
        "message": "Score processed successfully",
        "reward_kpi": reward_kpi,
        "reward_chips": reward_chips,
        "new_balance": current_user.kpi_current,
        "new_chips": profile.chip_balance
    }

    return {
        "message": "Score processed successfully",
        "reward_kpi": reward_kpi,
        "reward_chips": reward_chips,
        "new_balance": current_user.kpi_current,
        "new_chips": profile.chip_balance
    }

@router.get("/leaderboard/{game_type}")
async def get_leaderboard(
    game_type: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard for a specific game type"""
    # Mock data for now
    mock_leaderboard = [
        {"username": "Player1", "score": 1000, "date": "2024-01-15"},
        {"username": "Player2", "score": 950, "date": "2024-01-14"},
        {"username": "Player3", "score": 900, "date": "2024-01-13"},
        {"username": current_user.username, "score": 850, "date": "2024-01-12"},
    ]
    return {
        "game_type": game_type,
        "leaderboard": mock_leaderboard[:limit],
        "user_rank": 4
    }
