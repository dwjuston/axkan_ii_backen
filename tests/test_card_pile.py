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
    
    # Verify no sevens in draw pile and cards are sorted by rank
    for suit, cards in pile.get_draw_pile().items():
        assert len(cards) == 12  # 12 cards per suit (2-6,8-K)
        for card in cards:
            assert card.rank != CardRank.SEVEN
        # Verify cards are sorted by rank
        ranks = [card.rank.value for card in cards]
        assert ranks == sorted(ranks)


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
    
    # Draw until empty
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


def test_shuffle_discard_into_draw():
    """Test shuffling discard pile back into draw pile."""
    pile = CardPile()
    
    # Draw and discard some cards
    pair = pile.draw_pair()
    pile.discard_pair(pair)
    initial_draw_size = pile.draw_pile_size
    initial_discard_size = pile.discard_pile_size
    
    # Shuffle discard into draw
    pile.shuffle_discard_into_draw()
    assert pile.discard_pile_size == 0
    assert pile.draw_pile_size == initial_draw_size + initial_discard_size
    
    # Verify cards are back in their sorted positions
    for suit, cards in pile.get_draw_pile().items():
        ranks = [card.rank.value for card in cards]
        assert ranks == sorted(ranks)


def test_get_piles():
    """Test getting copies of piles."""
    pile = CardPile()
    
    # Get copies of piles
    draw_pile = pile.get_draw_pile()
    discard_pile = pile.get_discard_pile()
    
    # Verify copies are independent
    for suit in CardSuit:
        draw_pile[suit].pop()
        assert len(draw_pile[suit]) != len(pile.draw_pile[suit])
    
    discard_pile.append(Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG))
    assert len(discard_pile) != pile.discard_pile_size 