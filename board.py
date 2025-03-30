from pydantic import BaseModel
from typing import List, Optional
from player import Player
from card import CardPair
from enums.game_phase import GamePhase

class Board(BaseModel):
    """Game board state with player-specific view"""
    # Common game state
    dice_result: Optional[int]
    stock_price: Optional[int] = None
    turn_number: int
    available_pairs: List[CardPair]
    
    # Player roles
    first_selector: str  # player name
    second_selector: str  # player name
    dice_roller: str  # player name
    
    # Current player's data (from Player model)
    current_player: Player
    
    # Opponent's visible data
    opponent: Player  # but with hidden_pairs filtered out
    
    # Game phase
    current_phase: GamePhase
    
    # Selected pairs in current turn
    selected_pairs: List[CardPair]  # Empty list if no selection yet
