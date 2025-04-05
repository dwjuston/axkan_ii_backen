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
    game_id: str
    player_uuid: str

class PlayerMetadata(BaseModel):
    game_id: str
    player_uuid: str
    player_name: str
    opponent_uuid: Optional[str]
    opponent_name: Optional[str]

class GameMessage(BaseModel):
    board: Board

class GameError(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] 