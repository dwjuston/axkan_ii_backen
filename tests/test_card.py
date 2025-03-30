"""
Unit tests for card functionality.
"""
import pytest

from card import (
    Card,
    CardPair,
    CardSuit,
    CardRank,
    CardType
)


def test_card_creation():
    """Test basic card creation."""
    # Test red card
    hearts_ace = Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL)
    assert hearts_ace.is_red is True
    assert hearts_ace.is_black is False

    # Test black card
    spades_king = Card(suit=CardSuit.SPADES, rank=CardRank.KING, card_type=CardType.BIG)
    assert spades_king.is_red is False
    assert spades_king.is_black is True


def test_card_value_calculation():
    """Test card value calculation based on stock price."""
    # Test red card (value = max(stock_price - rank, 0))
    hearts_king = Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    assert hearts_king.get_value(20) == 7  # max(20 - 13, 0) = 7
    assert hearts_king.get_value(10) == 0  # max(10 - 13, 0) = 0

    # Test black card (value = max(rank - stock_price, 0))
    spades_king = Card(suit=CardSuit.SPADES, rank=CardRank.KING, card_type=CardType.BIG)
    assert spades_king.get_value(10) == 3  # max(13 - 10, 0) = 3
    assert spades_king.get_value(15) == 0  # max(13 - 15, 0) = 0


def test_card_color_conversion():
    """Test card color conversion."""
    # Test hearts ↔ spades
    hearts_ace = Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL)
    spades_ace = hearts_ace.convert_color()
    assert spades_ace.suit == CardSuit.SPADES
    assert spades_ace.rank == CardRank.ACE
    assert spades_ace.card_type == CardType.SMALL

    # Test diamonds ↔ clubs
    diamonds_king = Card(suit=CardSuit.DIAMONDS, rank=CardRank.KING, card_type=CardType.BIG)
    clubs_king = diamonds_king.convert_color()
    assert clubs_king.suit == CardSuit.CLUBS
    assert clubs_king.rank == CardRank.KING
    assert clubs_king.card_type == CardType.BIG


def test_card_pair_creation():
    """Test card pair creation and validation."""
    # Valid pair
    small_card = Card(suit=CardSuit.HEARTS, rank=CardRank.TWO, card_type=CardType.SMALL)
    big_card = Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    pair = CardPair(small_card=small_card, big_card=big_card)

    assert pair.cost == 2  # TWO = 2
    assert pair.get_pnl(20) == 5  # max(20 - 13, 0) - 2 = 5
    assert pair.get_pnl(10) == -2  # max(10 - 13, 0) - 2 = -2

    # Test black card pair
    black_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.SPADES, rank=CardRank.KING, card_type=CardType.BIG)
    )
    assert black_pair.get_pnl(10) == 1  # max(13 - 10, 0) - 2 = 1
    assert black_pair.get_pnl(15) == -2  # max(13 - 15, 0) - 2 = -2

    # Invalid pair - both small
    with pytest.raises(ValueError):
        CardPair(
            small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL),
            big_card=Card(suit=CardSuit.SPADES, rank=CardRank.SIX, card_type=CardType.SMALL)
        )

    # Invalid pair - both big
    with pytest.raises(ValueError):
        CardPair(
            small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG),
            big_card=Card(suit=CardSuit.SPADES, rank=CardRank.QUEEN, card_type=CardType.BIG)
        )


def test_breakeven_price():
    """Test breakeven price calculation."""
    # Red big card
    pair_red = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )
    assert pair_red.get_breakeven_price() == 14  # 13 + 1
    assert pair_red.get_breakeven_price_str() == ">=14"

    # Black big card
    pair_black = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.SPADES, rank=CardRank.KING, card_type=CardType.BIG)
    )
    assert pair_black.get_breakeven_price() == 12  # 13 - 1
    assert pair_black.get_breakeven_price_str() == "<=12"


def test_big_card_color_conversion():
    """Test big card color conversion in a pair."""
    pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )

    converted_pair = pair.convert_big_card_color()
    assert converted_pair.small_card.suit == CardSuit.HEARTS  # small card unchanged
    assert converted_pair.big_card.suit == CardSuit.SPADES  # big card converted
    assert converted_pair.big_card.rank == CardRank.KING  # rank unchanged
