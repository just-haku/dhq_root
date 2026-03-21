from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel
from typing import List, Tuple, Optional
import random

router = APIRouter()

class BovoMove(BaseModel):
    board_size: int = 50
    stones: List[Tuple[int, int, str]]  # [(x, y, color), ...]
    difficulty: str = "MEDIUM"

def get_board_dict(stones):
    return {(x, y): color for x, y, color in stones}

def check_win(board_dict, x, y, color, board_size):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        # Positive direction
        for i in range(1, 5):
            if board_dict.get((x + dx*i, y + dy*i)) == color:
                count += 1
            else:
                break
        # Negative direction
        for i in range(1, 5):
            if board_dict.get((x - dx*i, y - dy*i)) == color:
                count += 1
            else:
                break
        if count >= 5:
            return True
    return False

def score_position(board_dict, x, y, color):
    """Simple heuristic for Gomoku"""
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        line = []
        for i in range(-4, 5):
            line.append(board_dict.get((x + dx*i, y + dy*i)))
        
        # Look for patterns (simplified)
        line_str = "".join(['.' if v is None else ('1' if v == color else '2') for v in line])
        if '11111' in line_str: score += 100000
        if '.1111.' in line_str: score += 10000
        if '.111.' in line_str: score += 1000
        if '.11.' in line_str: score += 100
        
        # Block opponent
        opp_color = 'white' if color == 'black' else 'black'
        opp_line_str = "".join(['.' if v is None else ('1' if v == opp_color else '2') for v in line])
        if '11111' in opp_line_str: score += 50000
        if '.1111.' in opp_line_str: score += 5000
    return score

@router.post("/move")
async def get_bovo_move(
    request: BovoMove,
    current_user: User = Depends(get_current_user)
):
    """Calculate AI move for Bovo (Gomoku)"""
    board_dict = get_board_dict(request.stones)
    board_size = request.board_size
    difficulty = request.difficulty.upper()
    
    if not request.stones:
        # First move in center-ish
        return {"move": (board_size // 2, board_size // 2)}
    
    # Define search area around existing stones
    min_x = min(x for x, y, c in request.stones) - 2
    max_x = max(x for x, y, c in request.stones) + 2
    min_y = min(y for x, y, c in request.stones) - 2
    max_y = max(y for x, y, c in request.stones) + 2
    
    # Clip to board size
    min_x, max_x = max(0, min_x), min(board_size-1, max_x)
    min_y, max_y = max(0, min_y), min(board_size-1, max_y)
    
    best_move = None
    best_score = -1
    
    moves_to_check = []
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if (x, y) not in board_dict:
                moves_to_check.append((x, y))
    
    if difficulty == "EASY":
        best_move = random.choice(moves_to_check)
    else:
        # AI plays as 'white' (assuming user is 'black')
        ai_color = 'white'
        for x, y in moves_to_check:
            score = score_position(board_dict, x, y, ai_color)
            if score > best_score:
                best_score = score
                best_move = (x, y)
            elif score == best_score:
                if random.random() < 0.5:
                    best_move = (x, y)
    
    # If no move found, pick random
    if not best_move:
        best_move = random.choice(moves_to_check)
        
    return {"move": best_move}
