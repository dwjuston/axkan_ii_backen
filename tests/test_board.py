import pytest
from game_context import GameContext
from player import Player
from card import Card, CardPair, CardSuit, CardRank, CardType
from enums.game_phase import GamePhase
from board import Board

@pytest.fixture
def game_context():
    context = GameContext()
    # Create two players
    p1 = Player(player_id="player1")
    p2 = Player(player_id="player2")
    context.add_player(p1)
    context.add_player(p2)
    # Set initial price for all tests
    context.current_price = 10
    return context

@pytest.fixture
def sample_card_pair():
    small_card = Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL)
    big_card = Card(suit=CardSuit.SPADES, rank=CardRank.KING, card_type=CardType.BIG)
    return CardPair(small_card=small_card, big_card=big_card)

def test_board_creation(game_context, sample_card_pair):
    """Test creating a board for a player"""
    # Set up game state
    game_context.current_phase = GamePhase.TURN_SELECT_FIRST
    game_context.current_turn = 1
    game_context.available_pairs = [sample_card_pair]
    game_context.first_selector = game_context.players[0]
    
    # Create board for player1
    board = game_context.create_board_for_player("player1")
    
    # Verify board data
    assert isinstance(board, Board)
    assert board.stock_price == 10
    assert board.turn_number == 1
    assert len(board.available_pairs) == 1
    assert board.first_selector == "player1"
    assert board.current_phase == GamePhase.TURN_SELECT_FIRST
    assert board.current_player.player_id == "player1"
    assert board.opponent.player_id == "player2"

def test_board_hidden_pairs_filtering(game_context, sample_card_pair):
    """Test that opponent's hidden pairs are filtered out"""
    # Set up game state
    game_context.current_phase = GamePhase.TURN_SELECT_FIRST
    # Add hidden pair to player2 through portfolio
    game_context.players[1].portfolio.add_hidden_pair(sample_card_pair)
    
    # Create board for player1
    board = game_context.create_board_for_player("player1")
    
    # Verify player1 doesn't see player2's hidden pairs
    assert len(board.opponent.portfolio.get_hidden_pairs()) == 0

def test_board_selected_pairs(game_context, sample_card_pair):
    """Test that selected pairs are included in the board"""
    # Set up game state
    game_context.current_phase = GamePhase.TURN_SELECT_SECOND
    game_context.selected_pairs = [sample_card_pair]
    
    # Create board for player1
    board = game_context.create_board_for_player("player1")
    
    # Verify selected pairs are included
    assert len(board.selected_pairs) == 1
    assert board.selected_pairs[0] == sample_card_pair

def test_board_invalid_player(game_context):
    """Test creating board for non-existent player"""
    with pytest.raises(ValueError, match="Player invalid_id not found in game"):
        game_context.create_board_for_player("invalid_id")

def test_board_roles(game_context):
    """Test that player roles are correctly set"""
    # Set up game state
    game_context.current_phase = GamePhase.TURN_SELECT_FIRST
    game_context.first_selector = game_context.players[0]
    
    # Create board for player1
    board = game_context.create_board_for_player("player1")
    
    # Verify roles
    assert board.first_selector == "player1"
    assert board.second_selector == "player2"
    assert board.dice_roller == "player2"  # Second selector is dice roller 