"""
Tests for the Player class.
"""
import pytest

from card import Card, CardPair, CardSuit, CardRank, CardType
from player import Player


@pytest.fixture
def player():
    """Create a player for testing."""
    return Player(uuid="1", player_id=1, name="Player 1")


@pytest.fixture
def sample_pair():
    """Create a sample card pair for testing."""
    big_card = Card(suit=CardSuit.HEARTS, rank=CardRank.KING)
    small_card = Card(suit=CardSuit.SPADES, rank=CardRank.TWO)
    return CardPair(big_card=big_card, small_card=small_card)


def test_player_initialization(player):
    """Test player initialization."""
    assert player.uuid == "1"
    assert player.player_id == 1
    assert player.name == "Player 1"
    assert len(player.selected_pairs) == 0
    assert len(player.seven_cards) == 0
    assert player.hidden_pair is None


def test_select_pair(player, sample_pair):
    """Test selecting a pair."""
    # First selection should succeed
    player.select_pair(sample_pair)
    assert len(player.selected_pairs) == 1
    assert player.selected_pairs[0] == sample_pair


def test_seven_card_operations(player):
    """Test seven card operations."""
    # Create a seven card
    seven_card = Card(suit=CardSuit.HEARTS, rank=CardRank.SEVEN)
    player.portfolio.add_seven_card(seven_card)
    
    # Check seven card property
    assert len(player.seven_cards) == 1
    assert player.seven_cards[0] == seven_card
    
    # Use seven card
    special_card = player.seven_cards[0]
    player.remove_seven_card(special_card)
    assert len(player.seven_cards) == 0



def test_convert_card_color(player, sample_pair):
    """Test card color conversion."""
    # Add a seven card and a pair
    seven_card = Card(suit=CardSuit.HEARTS, rank=CardRank.SEVEN)
    player.portfolio.add_seven_card(seven_card)
    player.select_pair(sample_pair)
    
    # Convert color
    original_suit = sample_pair.big_card.suit

    assert player.convert_card_color(sample_pair, 0)
    # Check that the pair in portfolio was updated
    assert player.selected_pairs[0].big_card.suit != original_suit



def test_player_model(player, sample_pair):
    """Test PnL calculation."""
    # Add a pair
    player.select_pair(sample_pair)
    
    player_model = player.model_dump()
    assert list(player_model.keys()) == ["uuid", "player_id", "name", "portfolio"]
    assert player_model["uuid"] == "1"
    assert player_model["player_id"] == 1
    assert player_model["name"] == "Player 1"

def test_opponent_view(player, sample_pair):
    """Test opponent view."""
    # Add a pair
    player.select_pair(sample_pair)

    opponent_view = player.get_opponent_view(20)
    assert opponent_view.uuid == "1"
    assert opponent_view.name == "Player 1"
    assert opponent_view.player_id == 1
    assert opponent_view.selected_pairs == player.selected_pairs
    assert opponent_view.cost == player.get_cost()
    assert opponent_view.value == player.get_value(20)
    assert opponent_view.pnl == player.get_pnl(20)

def test_player_view(player, sample_pair):
    """Test player view."""
    # Add a pair
    player.select_pair(sample_pair)

    player_view = player.get_player_view(20)
    assert player_view.uuid == "1"
    assert player_view.name == "Player 1"
    assert player_view.player_id == 1
    assert player_view.selected_pairs == player.selected_pairs
    assert player_view.seven_cards == player.seven_cards
    assert player_view.hidden_pair == player.hidden_pair
    assert player_view.cost == player.get_cost()
    assert player_view.value == player.get_value(20)
    assert player_view.pnl == player.get_pnl(20)
