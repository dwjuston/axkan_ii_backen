from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class NotificationType(str, Enum):
    # Game State
    GAME_STARTED = "game_started"
    GAME_STARTED_INITIAL = "game_started_initial"
    GAME_ENDED = "game_ended"
    GAME_ERROR = "game_error"
    
    # Player Events
    PLAYER_SELECTING = "player_selecting"
    OPPONENT_SELECTING = "opponent_selecting"
    TURN_COMPLETE = "turn_complete"


    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    PLAYER_TURN = "player_turn"
    
    # Game Actions
    DICE_ROLLED = "dice_rolled"
    PIECE_MOVED = "piece_moved"
    INVALID_MOVE = "invalid_move"

class Notification(BaseModel):
    type: NotificationType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    game_id: str  # Required for routing
    target_players: Optional[List[str]] = None  # Optional list of player IDs 