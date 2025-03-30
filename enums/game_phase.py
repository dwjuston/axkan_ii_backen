from enum import Enum, auto

class GamePhase(Enum):
    LOBBY = auto()
    GAME_START = auto()
    GAME_INIT = auto()
    TURN_START = auto()
    TURN_SELECT_FIRST = auto()
    TURN_SELECT_SECOND = auto()
    TURN_COMPLETE = auto()
    FINAL_REVIEW = auto() # Allow color conversion
    GAME_END = auto() 