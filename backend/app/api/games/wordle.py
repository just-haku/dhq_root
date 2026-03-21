from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import random

router = APIRouter()

class WordleGuessRequest(BaseModel):
    guess: str

# Expanded dictionary as requested by user
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
    "DRANK", "DRAWN", "DREAM", "DRESS", "DRIED", "DRILL", "DRINK", "DRIVE", "DROVE", "DYING",
    "EAGLE", "EARLY", "EARTH", "EIGHT", "ELITE", "EMPTY", "ENEMY", "ENJOY", "ENTER", "ENTRY",
    "EQUAL", "ERROR", "EVENT", "EVERY", "EXACT", "EXIST", "EXTRA", "FAITH", "FALSE", "FAULT",
    "FIELD", "FIFTH", "FIFTY", "FINAL", "FIRST", "FIXED", "FLASH", "FLEET", "FLOOR", "FLUID",
    "FOCUS", "FORCE", "FORTH", "FORTY", "FORUM", "FOUND", "FRAME", "FRANK", "FRAUD", "FRESH",
    "FRONT", "FRUIT", "FULLY", "FUNNY", "GIANT", "GIVEN", "GLASS", "GLOVE", "GOING", "GRACE",
    "GRADE", "GRAND", "GRANT", "GRASS", "GREAT", "GREEN", "GROSS", "GROUP", "GROWN", "GUARD",
    "GUESS", "GUEST", "GUIDE", "HABIT", "HAPPY", "HEART", "HEAVY", "HENCE", "HENRY", "HORSE",
    "HOTEL", "HOUSE", "HUMAN", "IDEAL", "IMAGE", "INDEX", "INNER", "INPUT", "INTEL", "INTER",
    "JOINT", "JUDGE", "KNOWN", "LABEL", "LARGE", "LASER", "LATER", "LAUGH", "LAYER", "LEARN",
    "LEASE", "LEAST", "LEAVE", "LEGAL", "LEVEL", "LIGHT", "LIMIT", "LINKS", "LIVES", "LOCAL",
    "LOGIC", "LOOSE", "LOWER", "LUCKY", "LUNCH", "LYING", "MAGIC", "MAJOR", "MAKER", "MARCH",
    "MATCH", "MAYBE", "MAYOR", "MEDIA", "METAL", "MIGHT", "MINOR", "MINUS", "MIXED", "MODEL",
    "MONEY", "MONTH", "MORAL", "MOTOR", "MOUNT", "MOUSE", "MOUTH", "MOVIE", "MUSIC", "NEEDS",
    "NEVER", "NEWLY", "NIGHT", "NOISE", "NORTH", "NOTED", "NOVEL", "NURSE", "OCCUR", "OCEAN",
    "OFFER", "OFTEN", "ORDER", "OTHER", "OUGHT", "PAINT", "PANEL", "PAPER", "PARTY", "PEACE",
    "PETER", "PHASE", "PHONE", "PHOTO", "PIECE", "PILOT", "PITCH", "PLACE", "PLAIN", "PLANE",
    "PLANT", "PLATE", "POINT", "POUND", "POWER", "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT",
    "PRIOR", "PRIZE", "PROOF", "PROUD", "PROVE", "QUEEN", "QUICK", "QUIET", "QUITE", "RADIO",
    "RAISE", "RANGE", "RAPID", "RATIO", "REACH", "READY", "REFER", "RIGHT", "RIVAL", "RIVER",
    "ROBIN", "ROGER", "ROMAN", "ROUGH", "ROUND", "ROUTE", "ROYAL", "RURAL", "SCALE", "SCENE",
    "SCOPE", "SCORE", "SENSE", "SERVE", "SEVEN", "SHALL", "SHAPE", "SHARE", "SHARP", "SHEET",
    "SHELF", "SHELL", "SHIFT", "SHIRT", "SHOCK", "SHOOT", "SHORT", "SHOWN", "SIGHT", "SINCE",
    "SIXTH", "SIXTY", "SIZED", "SKILL", "SLEEP", "SLIDE", "SMALL", "SMART", "SMILE", "SMITH",
    "SMOKE", "SOLID", "SOLVE", "SORRY", "SOUND", "SOUTH", "SPACE", "SPARE", "SPEAK", "SPEED",
    "SPEND", "SPENT", "SPLIT", "SPOKE", "SPORT", "STAFF", "STAGE", "STAKE", "STAND", "START",
    "STATE", "STEAM", "STEEL", "STICK", "STILL", "STOCK", "STONE", "STOOD", "STORE", "STORM",
    "STORY", "STRIP", "STUCK", "STUDY", "STUFF", "STYLE", "SUGAR", "SUITE", "SUPER", "SWEET",
    "TABLE", "TAKEN", "TASTE", "TAXES", "TEACH", "TEETH", "TEXAS", "THANK", "THEFT", "THEIR",
    "THEME", "THERE", "THESE", "THICK", "THING", "THINK", "THIRD", "THOSE", "THREE", "THREW",
    "THROW", "TIGHT", "TIMES", "TITLE", "TODAY", "TOKEN", "TOTAL", "TOUCH", "TOUGH", "TOWER",
    "TRACK", "TRADE", "TRAIN", "TREAT", "TREND", "TRIAL", "TRIED", "TRIES", "TRUCK", "TRULY",
    "TRUST", "TRUTH", "TWICE", "UNDER", "UNDUE", "UNION", "UNITY", "UNTIL", "UPPER", "UPSET",
    "URBAN", "USAGE", "USUAL", "VALID", "VALUE", "VIDEO", "VIRUS", "VISIT", "VITAL", "VOICE",
    "WASTE", "WATCH", "WATER", "WHEEL", "WHERE", "WHICH", "WHILE", "WHITE", "WHOLE", "WHOSE",
    "WOMAN", "WOMEN", "WORLD", "WORRY", "WORSE", "WORST", "WORTH", "WRITE", "WRONG", "WROTE",
    "YIELD", "YOUNG", "YOUTH"
]

@router.post("/new")
async def start_wordle_game(current_user: User = Depends(get_current_user)):
    """Start a new Wordle game"""
    word = random.choice(WORDLE_WORDS)
    game_id = f"wordle_{current_user.id}_{datetime.utcnow().timestamp()}"
    return {
        "game_id": game_id,
        "word_length": len(word),
        "max_attempts": 6,
        "word": word
    }

@router.post("/guess")
async def make_wordle_guess(
    request: WordleGuessRequest,
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """Make a guess in Wordle game"""
    guess = request.guess.upper()
    if len(guess) != 5:
        raise HTTPException(status_code=400, detail="Guess must be 5 letters")
    
    # In a real app, you'd store the target_word in Redis or DB associated with game_id
    # For now, we'll use a mocked fixed word or consistent selection based on game_id
    # To keep it simple for this session, we'll use a predictable word based on game_id
    # (Real implementation should use session state)
    try:
        seed_str = game_id.split('_')[-1]
        local_random = random.Random(float(seed_str))
        target_word = local_random.choice(WORDLE_WORDS)
    except (ValueError, IndexError, TypeError):
        # Fallback if game_id is malformed
        target_word = random.choice(WORDLE_WORDS)
    
    result = [None] * 5
    target_chars = list(target_word)
    
    # First pass: Green (correct)
    for i in range(5):
        if guess[i] == target_word[i]:
            result[i] = {"letter": guess[i], "status": "correct"}
            target_chars[i] = None
            
    # Second pass: Yellow (present) or Gray (absent)
    for i in range(5):
        if result[i] is not None:
            continue
            
        letter = guess[i]
        if letter in target_chars:
            result[i] = {"letter": letter, "status": "present"}
            target_chars[target_chars.index(letter)] = None
        else:
            result[i] = {"letter": letter, "status": "absent"}
    
    is_win = guess == target_word
    # Need to track attempts somehow, but for now we'll assume the frontend 
    # provides game_over status or we just check if it's a win.
    # To truly track 6 attempts we'd need session state.
    
    kpi_reward = 0
    if is_win:
        kpi_reward = 50
    
    if kpi_reward > 0:
        old_balance = current_user.kpi_current
        current_user.kpi_current += kpi_reward
        current_user.save()
        print(f"DEBUG: Wordle Reward Awarded to {current_user.username}")
        print(f"       Amount: {kpi_reward} KPI")
        print(f"       Balance: {old_balance} -> {current_user.kpi_current}")
        
        KPIHistory(
            user=current_user,
            amount=kpi_reward,
            balance_after=current_user.kpi_current,
            source="wordle_win",
            reason="Won Wordle game"
        ).save()
    
    response_data = {
        "result": result,
        "is_win": is_win,
        "game_over": is_win,
        "new_balance": current_user.kpi_current
    }
    print(f"DEBUG: Wordle API Response for {current_user.username}: {response_data}")
    return response_data
