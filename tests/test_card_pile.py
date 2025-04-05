"""
Tests for the CardPile class.
"""
import pytest
from card import Card, CardPair, CardSuit, CardRank, CardType
from card_pile import CardPile


def test_card_pile_initialization():
    """Test card pile initialization."""
    pile = CardPile()
    
    # Check draw pile size (48 cards: 4 suits * (2-6,8-K) = 4 * 12 = 48)
    assert pile.draw_pile_size == 48
    
    # Check discard pile is empty
    assert pile.discard_pile_size == 0



def test_draw_pair():
    """Test drawing card pairs."""
    pile = CardPile()
    initial_size = pile.draw_pile_size
    
    # Draw a pair
    pair = pile.draw_pair()
    assert pair is not None
    assert isinstance(pair, CardPair)
    assert pair.small_card.card_type == CardType.SMALL
    assert pair.big_card.card_type == CardType.BIG
    assert pile.draw_pile_size == initial_size - 2
    
    # Get error when trying to draw from empty pile
    while pile.draw_pair():
        pass
    assert pile.draw_pile_size == 0
    
    # Try to draw from empty pile
    assert pile.draw_pair() is None


def test_discard_pair():
    """Test discarding card pairs."""
    pile = CardPile()
    
    # Draw and discard a pair
    pair = pile.draw_pair()
    assert pair is not None
    initial_discard_size = pile.discard_pile_size
    
    pile.discard_pair(pair)
    assert pile.discard_pile_size == initial_discard_size + 2
    assert pair.small_card in pile.get_discard_pile()
    assert pair.big_card in pile.get_discard_pile()