from enum import Enum, auto

class GameAction(Enum):
    # Lobby Actions
    JOIN_GAME = auto()
    READY = auto()
    START_GAME = auto()
    INITIALIZE_GAME = auto()
    
    # Roll Actions (includes both regular and special rolls)
    ROLL_DICE = auto()

    # Selection Actions
    SELECT_PAIR = auto()
    
    # Special Actions
    COLOR_CONVERT = auto()
    
    # End Game Actions
    CALCULATE_SCORES = auto()
    RETURN_TO_LOBBY = auto() 