from pydantic import BaseModel
from typing import List, Optional, Dict
from player import Player, PlayerView, OpponentView
from card import CardPair
from enums.game_phase import GamePhase

class Board(BaseModel):
    """Game board state with player-specific view"""
    # Common game state
    current_phase: GamePhase
    turn_number: int
    dice_result: List[int]
    dice_extra: int = 0
    stock_price: Optional[int]

    # Player roles
    first_selector: Optional[int]  # player id
    second_selector: Optional[int]  # player id
    dice_roller: Optional[int]  # player id

    # Card Pairs
    available_pairs: List[CardPair]
    selected_pair_index: Dict[str, int]  # player uuid -> pair index

    # Current player's data (from Player model)
    current_player: PlayerView
    
    # Opponent's visible data
    opponent: OpponentView

    @staticmethod
    def create_sample():
        return {
            'current_phase': GamePhase.TURN_SELECT_FIRST,
            'turn_number': 1,
            'dice_result': [4, -4],
            'dice_extra': 0,
            'stock_price': 10,
            'first_selector': 1,
            'second_selector': 2,
            'dice_roller': 2,
            'available_pairs': [
                {
                    'small_card': {
                        'suit': 'HEARTS',
                        'rank': 'ACE'
                    },
                    'big_card': {
                        'suit': 'SPADES',
                        'rank': 'KING'
                    }
                }
            ],
            'selected_pair_index': {},
            'current_player': {
                'uuid': '1',
                'player_id': 1,
                'name': 'Player 1',
                'selected_pairs': [],
                'seven_cards': [],
                'hidden_pair': None,
                'pnl': 0,
                'cost': 0,
                'value': 0
            },
            'opponent': {
                'uuid': '2',
                'name': 'Player 2',
                'player_id': 2,
                'selected_pairs': [],
                'seven_cards': [],
                'pnl': 0,
                'cost': 0,
                'value': 0
            }
        }
