from enum import Enum, auto

class GameAction(Enum):
    # Lobby Actions
    JOIN_GAME = "join_game"
    READY = "ready"
    START_GAME = "start_game"
    INITIALIZE_GAME = "initialize_game"
    
    # Roll Actions (includes both regular and special rolls)
    ROLL_DICE = "roll_dice"

    # Selection Actions
    SELECT_PAIR = "select_pair"
    
    # Special Actions
    COLOR_CONVERT = "color_convert"
    END_REVIEW = "end_review"
    
    # End Game Actions
    CALCULATE_SCORES = "calculate_scores"
    RETURN_TO_LOBBY = "return_to_lobby"