from enum import Enum, auto

class GameAction(Enum):
    JOIN_GAME = "join_game"
    READY = "ready"
    ROLL_DICE = "roll_dice"
    SELECT_PAIR = "select_pair"
    COLOR_CONVERT = "color_convert"
    END_REVIEW = "end_review"
    RETURN_TO_LOBBY = "return_to_lobby"