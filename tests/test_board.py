import pytest
from game_context import GameContext
from player import Player
from card import Card, CardPair, CardSuit, CardRank, CardType
from enums.game_phase import GamePhase
from board import Board

@pytest.fixture
def player1():
    return Player(uuid="1", player_id=1, name="Player 1")

@pytest.fixture
def player2():
    return Player(uuid="2", player_id=2, name="Player 2")

@pytest.fixture
def sample_card_pair():
    small_card = Card(suit=CardSuit.HEARTS, rank=CardRank.ACE)
    big_card = Card(suit=CardSuit.SPADES, rank=CardRank.KING)
    return CardPair(small_card=small_card, big_card=big_card)

def test_board_creation(player1, player2, sample_card_pair):
    """Test creating a board for a player"""

    # Create board
    board = Board(
        current_phase=GamePhase.TURN_SELECT_FIRST,
        turn_number=1,
        dice_result=[4, -4],
        dice_extra=0,
        stock_price=10,
        first_selector=player1.player_id,
        second_selector=player2.player_id,
        dice_roller=player2.player_id,
        available_pairs=[sample_card_pair],
        selected_pair_index={},
        current_player=player1.get_player_view(10),
        opponent=player2.get_opponent_view(10)
    )
    
    # Verify board data
    board_dict = board.model_dump()
    assert board_dict.keys() == {
        'current_phase', 'turn_number', 'dice_result', 'dice_extra', 'stock_price',
        'first_selector', 'second_selector', 'dice_roller', 'available_pairs',
        'selected_pair_index', 'current_player', 'opponent'
    }