from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import random
import string

router = APIRouter()

# Game models
class WordleGuessRequest(BaseModel):
    guess: str

class TypingTestRequest(BaseModel):
    text: str
    typed_text: str
    time_taken: float  # in seconds

class GameScore(BaseModel):
    game_type: str
    score: int
    metadata: dict = {}

# Wordle game logic
WORDLE_WORDS = [
    "ABOUT", "ABOVE", "ABUSE", "ACTOR", "ACUTE", "ADMIT", "ADOPT", "ADULT", "AFTER", "AGAIN",
    "AGENT", "AGREE", "AHEAD", "ALARM", "ALBUM", "ALERT", "ALIEN", "ALIGN", "ALIKE", "ALIVE",
    "ALLOW", "ALONE", "ALONG", "ALTER", "ANGEL", "ANGER", "ANGLE", "ANGRY", "APART", "APPLE",
    "APPLY", "ARENA", "ARGUE", "ARISE", "ARRAY", "ASIDE", "ASSET", "AVOID", "AWAKE", "AWARE",
    "BADGE", "BADLY", "BAKER", "BASES", "BASIC", "BEACH", "BEGAN", "BEING", "BELOW", "BENCH",
    "BILLY", "BIRTH", "BLACK", "BLAME", "BLIND", "BLOCK", "BLOOD", "BOARD", "BOOST", "BOOTH",
    "BOUND", "BRAIN", "BRAND", "BRAVE", "BREAD", "BREAK", "BREED", "BRIEF", "BRING", "BROAD",
    "BROKE", "BROWN", "BUILD", "BUILT", "BUYER", "CABLE", "CALIF", "CARRY", "CATCH", "CAUSE",
    "CHAIN", "CHAIR", "CHAOS", "CHARM", "CHART", "CHASE", "CHEAP", "CHECK", "CHEST", "CHIEF",
    "CHILD", "CHINA", "CHOSE", "CIVIL", "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLICK", "CLIMB",
    "CLOCK", "CLOSE", "CLOUD", "COACH", "COAST", "COULD", "COUNT", "COURT", "COVER", "CRAFT",
    "CRASH", "CRAZY", "CREAM", "CRIME", "CROSS", "CROWD", "CROWN", "CRUDE", "CURVE", "CYCLE",
    "DAILY", "DANCE", "DATED", "DEALT", "DEATH", "DEBUT", "DELAY", "DELTA", "DENSE", "DEPOT",
    "DEPTH", "DERBY", "DIGIT", "DIRTY", "DOESN", "DOING", "DOUBT", "DOZEN", "DRAFT", "DRAMA",
    "DRANK", "DRAWN", "DREAM", "DRESS", "DRIED", "DRILL", "DRINK", "DRIVE", "DROVE", "DYING"
]

# Typing test texts
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

@router.post("/wordle/new")
async def start_wordle_game(current_user: User = Depends(get_current_user)):
    """Start a new Wordle game"""
    word = random.choice(WORDLE_WORDS)
    
    # Store game session (in production, use Redis or database)
    game_id = f"wordle_{current_user.id}_{datetime.utcnow().timestamp()}"
    
    return {
        "game_id": game_id,
        "word_length": len(word),
        "max_attempts": 6,
        "word": word  # In production, don't return the word!
    }

@router.post("/wordle/guess")
async def make_wordle_guess(
    request: WordleGuessRequest,
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """Make a guess in Wordle game"""
    # In production, retrieve the actual word from session storage
    # For now, we'll simulate the logic
    
    guess = request.guess.upper()
    
    if len(guess) != 5:
        raise HTTPException(status_code=400, detail="Guess must be 5 letters")
    
    if guess not in WORDLE_WORDS and len(set(guess)) == 5:  # Basic validation
        # Allow valid 5-letter words even if not in our list
        pass
    elif len(set(guess)) != 5:
        raise HTTPException(status_code=400, detail="Invalid word")
    
    # Simulate word checking (in production, compare with stored word)
    # For demo, we'll use a random word
    target_word = "HELLO"  # This should come from session storage
    
    result = []
    for i, letter in enumerate(guess):
        if letter == target_word[i]:
            result.append({"letter": letter, "status": "correct"})
        elif letter in target_word:
            result.append({"letter": letter, "status": "present"})
        else:
            result.append({"letter": letter, "status": "absent"})
    
    is_win = guess == target_word
    
    if is_win:
        # Award KPI points for winning
        kpi_reward = 50
        current_user.kpi_current += kpi_reward
        current_user.save()
        
        KPIHistory(
            user=current_user,
            amount=kpi_reward,
            balance_after=current_user.kpi_current,
            source="wordle_win",
            reason="Won Wordle game"
        ).save()
    
    return {
        "result": result,
        "is_win": is_win,
        "game_over": is_win,
        "new_balance": current_user.kpi_current
    }

@router.post("/typing/start")
async def start_typing_test(current_user: User = Depends(get_current_user)):
    """Start a new typing test"""
    text = random.choice(TYPING_TEXTS)
    game_id = f"typing_{current_user.id}_{datetime.utcnow().timestamp()}"
    
    return {
        "game_id": game_id,
        "text": text,
        "start_time": datetime.utcnow().isoformat()
    }

@router.post("/typing/submit")
async def submit_typing_test(
    request: TypingTestRequest,
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """Submit typing test results"""
    text = request.text
    typed_text = request.typed_text
    time_taken = request.time_taken
    
    # Calculate metrics
    words = text.split()
    typed_words = typed_text.split()
    
    # Accuracy calculation
    correct_chars = sum(1 for i, char in enumerate(typed_text) if i < len(text) and char == text[i])
    accuracy = (correct_chars / len(text)) * 100 if text else 0
    
    # WPM calculation (standard: 5 characters = 1 word)
    characters_typed = len(typed_text)
    minutes_taken = time_taken / 60
    wpm = (characters_typed / 5) / minutes_taken if minutes_taken > 0 else 0
    
    # Score calculation
    base_score = int(wpm * 10 + accuracy)
    time_bonus = max(0, 100 - int(time_taken))
    total_score = base_score + time_bonus
    
    # Award KPI points based on performance
    kpi_reward = 0
    if accuracy >= 95 and wpm >= 60:
        kpi_reward = 30
    elif accuracy >= 90 and wpm >= 40:
        kpi_reward = 20
    elif accuracy >= 80 and wpm >= 30:
        kpi_reward = 10
    
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
        "performance_rating": get_typing_rating(wpm, accuracy)
    }

@router.post("/memory/start")
async def start_memory_game(current_user: User = Depends(get_current_user)):
    """Start a memory card game"""
    # Generate pairs of cards (emojis for simplicity)
    emojis = ["🎮", "🎯", "🎨", "🎭", "🎪", "🎫", "🎬", "🎤"]
    cards = emojis * 2  # Create pairs
    random.shuffle(cards)
    
    game_id = f"memory_{current_user.id}_{datetime.utcnow().timestamp()}"
    
    return {
        "game_id": game_id,
        "cards": cards,
        "moves": 0,
        "matches": 0,
        "start_time": datetime.utcnow().isoformat()
    }

@router.post("/memory/flip")
async def flip_memory_card(
    game_id: str,
    card_index: int,
    current_user: User = Depends(get_current_user)
):
    """Flip a card in memory game"""
    # In production, manage game state in session storage
    # For now, return a simulated response
    
    return {
        "card_index": card_index,
        "card_value": "🎮",  # This should come from game state
        "is_match": False,
        "moves": 1,
        "matches": 0,
        "game_complete": False
    }

@router.post("/scores/submit")
async def submit_game_score(
    score: GameScore,
    current_user: User = Depends(get_current_user)
):
    """Submit a game score for leaderboard"""
    # Store score in database (in production, create a GameScore model)
    
    # Award bonus KPI for high scores
    bonus_kpi = 0
    if score.game_type == "wordle" and score.score >= 100:
        bonus_kpi = 25
    elif score.game_type == "typing" and score.score >= 500:
        bonus_kpi = 20
    elif score.game_type == "memory" and score.score >= 200:
        bonus_kpi = 15
    
    if bonus_kpi > 0:
        current_user.kpi_current += bonus_kpi
        current_user.save()
        
        KPIHistory(
            user=current_user,
            amount=bonus_kpi,
            balance_after=current_user.kpi_current,
            source="game_bonus",
            reason=f"High score bonus in {score.game_type}"
        ).save()
    
    return {
        "message": "Score submitted successfully",
        "bonus_kpi": bonus_kpi,
        "total_kpi": current_user.kpi_current
    }

@router.get("/leaderboard/{game_type}")
async def get_leaderboard(
    game_type: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard for a specific game type"""
    # In production, query actual scores from database
    # For now, return mock data
    
    mock_leaderboard = [
        {"username": "Player1", "score": 1000, "date": "2024-01-15"},
        {"username": "Player2", "score": 950, "date": "2024-01-14"},
        {"username": "Player3", "score": 900, "date": "2024-01-13"},
        {"username": current_user.username, "score": 850, "date": "2024-01-12"},
    ]
    
    return {
        "game_type": game_type,
        "leaderboard": mock_leaderboard[:limit],
        "user_rank": 4  # Calculate actual rank
    }

def get_typing_rating(wpm: float, accuracy: float) -> str:
    """Get performance rating based on WPM and accuracy"""
    if accuracy >= 95 and wpm >= 80:
        return "Exceptional"
    elif accuracy >= 90 and wpm >= 60:
        return "Excellent"
    elif accuracy >= 85 and wpm >= 45:
        return "Good"
    elif accuracy >= 80 and wpm >= 35:
        return "Average"
    else:
        return "Needs Practice"
