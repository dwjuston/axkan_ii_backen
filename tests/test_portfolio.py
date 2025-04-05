"""
Test the Portfolio class.
"""
from card import CardPair, Card, CardSuit, CardRank, CardType
from portfolio import Portfolio

def test_portfolio_creation():
    """Test portfolio creation."""
    portfolio = Portfolio()
    assert portfolio.get_cost() == 0
    assert portfolio.get_value(20) == 0
    assert portfolio.get_pnl(20) == 0
    assert portfolio.hidden_pairs == []
    assert portfolio.regular_pairs == []
    assert portfolio.seven_cards == []

def test_portfolio_add_pair():
    """Test adding pairs to the portfolio."""
    portfolio = Portfolio()

    # Add hidden pair
    hidden_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING)
    )
    portfolio.add_hidden_pair(hidden_pair)
    assert portfolio.hidden_pairs == [hidden_pair]
    assert portfolio.regular_pairs == []

    # Add regular pair
    regular_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING)
    )
    portfolio.add_pair(regular_pair)
    assert portfolio.hidden_pairs == [hidden_pair]
    assert portfolio.regular_pairs == [regular_pair]

def test_portfolio_metrics():
    """Test portfolio metrics calculation."""
    portfolio = Portfolio()

    # Add a pair
    pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING)
    )
    portfolio.add_pair(pair)

    # Test total cost
    assert portfolio.get_cost() == 2

    # Test total value
    assert portfolio.get_value(20) == 7  # 20 - 13 = 7

    # Test profit and loss
    assert portfolio.get_pnl(20) == 5  # 7 - 2 = 5

def test_portfolio_model():
    """Test portfolio visibility."""
    portfolio = Portfolio()

    # Add a pair
    pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.TWO),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING)
    )
    portfolio.add_pair(pair)

    # Add a hidden pair
    hidden_pair = CardPair(
        small_card=Card(suit=CardSuit.HEARTS, rank=CardRank.ACE),
        big_card=Card(suit=CardSuit.HEARTS, rank=CardRank.KING)
    )
    portfolio.add_hidden_pair(hidden_pair)

    portfolio_dict = portfolio.model_dump()
    assert list(portfolio_dict.keys()) == ["regular_pairs", "hidden_pairs", "seven_cards"]
    assert portfolio_dict["regular_pairs"] == [pair.model_dump()]
    assert portfolio_dict["hidden_pairs"] == [hidden_pair.model_dump()]
    assert portfolio_dict["seven_cards"] == []