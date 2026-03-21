from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

class TicTacToeMove(BaseModel):
    board: List[Optional[str]]  # 9 elements, 'X', 'O', or None
    difficulty: str = "MEDIUM"

def check_winner(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # cols
        [0, 4, 8], [2, 4, 6]             # diagonals
    ]
    for line in lines:
        if board[line[0]] and board[line[0]] == board[line[1]] == board[line[2]]:
            return board[line[0]]
    if None not in board:
        return 'TIE'
    return None

def minimax(board, depth, is_maximizing):
    winner = check_winner(board)
    if winner == 'O': return 10 - depth
    if winner == 'X': return depth - 10
    if winner == 'TIE': return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] is None:
                board[i] = 'O'
                score = minimax(board, depth + 1, False)
                board[i] = None
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] is None:
                board[i] = 'X'
                score = minimax(board, depth + 1, True)
                board[i] = None
                best_score = min(score, best_score)
        return best_score

@router.post("/move")
async def get_ai_move(
    request: TicTacToeMove,
    current_user: User = Depends(get_current_user)
):
    """Calculate AI move for Tic Tac Toe"""
    board = request.board
    difficulty = request.difficulty.upper()
    
    if check_winner(board):
        raise HTTPException(status_code=400, detail="Game already over")
    
    available_moves = [i for i, val in enumerate(board) if val is None]
    
    if difficulty == "EASY":
        # Random move
        move = random.choice(available_moves)
    elif difficulty == "MEDIUM":
        # 50% chance of best move, else random
        if random.random() < 0.5:
            move = get_best_move(board)
        else:
            move = random.choice(available_moves)
    else: # HARD / EXTREME
        # Always best move
        move = get_best_move(board)
    
    return {"move": move}

def get_best_move(board):
    best_score = -float('inf')
    move = -1
    for i in range(9):
        if board[i] is None:
            board[i] = 'O'
            score = minimax(board, 0, False)
            board[i] = None
            if score > best_score:
                best_score = score
                move = i
    return move
