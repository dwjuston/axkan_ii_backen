"""
Test the Portfolio class.
"""
from card import CardPair, Card, CardSuit, CardRank, CardType
from portfolio import Portfolio

def test_portfolio_creation():
    """Test portfolio creation."""
    portfolio = Portfolio()
    assert portfolio.total_cost == 0
    assert portfolio.get_total_value(20) == 0
    assert portfolio.get_pnl(20) == 0
    assert portfolio.hidden_pair is None
    assert portfolio.regular_pairs == []

def test_portfolio_add_pair():
    """Test adding pairs to the portfolio."""
    portfolio = Portfolio()

    # Add hidden pair
    hidden_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )
    portfolio.add_hidden_pair(hidden_pair)
    assert portfolio.hidden_pair == hidden_pair
    assert portfolio.regular_pairs == []

    # Add regular pair
    regular_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )
    portfolio.add_pair(regular_pair)
    assert portfolio.hidden_pair == hidden_pair
    assert portfolio.regular_pairs == [regular_pair]

def test_portfolio_metrics():
    """Test portfolio metrics calculation."""
    portfolio = Portfolio()

    # Add a pair
    pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )
    portfolio.add_pair(pair)

    # Test total cost
    assert portfolio.total_cost == 2

    # Test total value
    assert portfolio.get_total_value(20) == 7  # 20 - 13 = 7

    # Test profit and loss
    assert portfolio.get_pnl(20) == 5  # 7 - 2 = 5

def test_portfolio_visibility():
    """Test portfolio visibility."""
    portfolio = Portfolio()

    # Add a pair
    pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )
    portfolio.add_pair(pair)

    # Add a hidden pair
    hidden_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE, card_type=CardType.SMALL),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING, card_type=CardType.BIG)
    )
    portfolio.add_hidden_pair(hidden_pair)

    # Test visible pairs
    assert portfolio.get_selected_pairs() == [pair]

    # Test all pairs
    assert portfolio.get_all_pairs() == [pair, hidden_pair]