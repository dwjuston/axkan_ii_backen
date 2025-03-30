from enum import Enum, auto

class GamePhase(Enum):
    LOBBY = "lobby"
    GAME_START = "game_start"
    GAME_INIT = "game_init"
    TURN_START = "turn_start"
    TURN_SELECT_FIRST = "turn_select_first"
    TURN_SELECT_SECOND = "turn_select_second"
    TURN_COMPLETE = "turn_complete"
    FINAL_REVIEW = "final_review"
    GAME_END = "game_end"