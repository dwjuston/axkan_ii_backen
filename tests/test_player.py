"""
Tests for the Player class.
"""
import pytest

from card import Card, CardPair, CardSuit, CardRank, CardType
from player import Player


@pytest.fixture
def player():
    """Create a player for testing."""
    return Player(player_id="1")


@pytest.fixture
def sample_pair():
    """Create a sample card pair for testing."""
    big_card = Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    small_card = Card(suit=CardSuit.SPADES, rank=CardRank.TWO, card_type=CardType.SMALL)
    return CardPair(big_card=big_card, small_card=small_card)


def test_player_initialization(player):
    """Test player initialization."""
    assert player.player_id == "1"
    assert not player.has_selected
    assert len(player.selected_pairs) == 0
    assert len(player.seven_cards) == 0
    assert len(player.hidden_pairs) == 0


def test_select_pair(player, sample_pair):
    """Test selecting a pair."""
    # First selection should succeed
    assert player.select_pair(sample_pair)
    assert player.has_selected
    assert len(player.selected_pairs) == 1
    assert player.selected_pairs[0] == sample_pair
    
    # Second selection in same turn should fail
    assert not player.select_pair(sample_pair)
    assert len(player.selected_pairs) == 1
    
    # Reset turn state
    player.reset_turn_state()
    assert not player.has_selected
    
    # Selection after reset should succeed
    assert player.select_pair(sample_pair)
    assert player.has_selected
    assert len(player.selected_pairs) == 2


def test_select_invalid_pair(player):
    """Test selecting invalid pairs."""
    # Selecting None should fail
    assert not player.select_pair(None)
    assert not player.has_selected
    assert len(player.selected_pairs) == 0


def test_seven_card_operations(player):
    """Test seven card operations."""
    # Create a seven card
    seven_card = Card(suit=CardSuit.HEARTS, rank=CardRank.SEVEN, card_type=CardType.SPECIAL)
    player.portfolio.add_seven_card(seven_card)
    
    # Check seven card property
    assert len(player.seven_cards) == 1
    assert player.seven_cards[0] == seven_card
    
    # Use seven card
    special_card = player.seven_cards[0]
    used_card = player.use_seven_card(special_card)
    assert used_card == seven_card
    assert len(player.seven_cards) == 0



def test_convert_card_color(player, sample_pair):
    """Test card color conversion."""
    # Add a seven card and a pair
    seven_card = Card(suit=CardSuit.HEARTS, rank=CardRank.SEVEN, card_type=CardType.SPECIAL)
    player.portfolio.add_seven_card(seven_card)
    player.select_pair(sample_pair)
    
    # Convert color
    original_suit = sample_pair.big_card.suit

    assert player.convert_card_color(sample_pair, 0)
    # Check that the pair in portfolio was updated
    assert player.selected_pairs[0].big_card.suit != original_suit



def test_get_pnl(player, sample_pair):
    """Test PnL calculation."""
    # Add a pair
    player.select_pair(sample_pair)
    
    # Test PnL calculation
    stock_price = 20
    pnl = player.get_pnl(stock_price)
    assert isinstance(pnl, int)
    # PnL should be big card value (7) minus cost (2)
    assert pnl == 5


def test_hidden_pairs(player, sample_pair):
    """Test hidden pairs functionality."""
    # Add a pair as hidden
    player.portfolio.add_hidden_pair(sample_pair)
    
    # Check hidden pairs
    assert len(player.hidden_pairs) == 1
    assert player.hidden_pairs[0] == sample_pair 