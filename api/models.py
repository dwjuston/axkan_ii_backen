from pydantic import BaseModel
from typing import List, Optional
from enums.game_action import GameAction
from board import Board

class JoinGameRequest(BaseModel):
    player_name: str

class GameMove(BaseModel):
    player_id: str
    move_type: GameAction
    move_data: dict

class GameMetadata(BaseModel):
    game_id: str
    status: str  # "waiting", "active", "ended"
    current_turn: int
    current_phase: str
    players: List[str]
    current_player: str

class GameResponse(BaseModel):
    status: str
    message: Optional[str]
    data: Optional[dict]

class GameError(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] 