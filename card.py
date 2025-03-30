"""
Card module for handling cards and card pairs in the game.
"""
from enum import Enum, auto
from typing import Optional
from pydantic import BaseModel, Field, validator

class CardSuit(Enum):
    """Types of card suits."""
    HEARTS = auto()
    DIAMONDS = auto()
    SPADES = auto()
    CLUBS = auto()

class CardRank(Enum):
    """Card ranks from Ace to King."""
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    SEVEN = 7  # Special card

class CardType(Enum):
    """Types of cards based on rank."""
    SMALL = auto()  # A-6
    BIG = auto()    # 8-K
    SPECIAL = auto() # 7

class Card(BaseModel):
    """Represents a single card in the game."""
    suit: CardSuit
    rank: CardRank
    card_type: CardType
    
    @property
    def is_red(self) -> bool:
        """Check if card is red (hearts or diamonds)."""
        return self.suit in (CardSuit.HEARTS, CardSuit.DIAMONDS)
    
    @property
    def is_black(self) -> bool:
        """Check if card is black (spades or clubs)."""
        return self.suit in (CardSuit.SPADES, CardSuit.CLUBS)
    
    def get_value(self, stock_price: int) -> int:
        """Calculate card value based on stock price."""
        if self.rank == CardRank.SEVEN:
            return 0  # Special card, no value
            
        rank_value = self.rank.value
        if self.is_red:
            return max(stock_price - rank_value, 0)
        else:  # black
            return max(rank_value - stock_price, 0)
    
    def convert_color(self) -> 'Card':
        """Convert card color (hearts ↔ spades, diamonds ↔ clubs)."""
        new_suit = {
            CardSuit.HEARTS: CardSuit.SPADES,
            CardSuit.SPADES: CardSuit.HEARTS,
            CardSuit.DIAMONDS: CardSuit.CLUBS,
            CardSuit.CLUBS: CardSuit.DIAMONDS
        }[self.suit]
        return Card(suit=new_suit, rank=self.rank, card_type=self.card_type)

class CardPair(BaseModel):
    """Represents a pair of cards (small + big)."""
    small_card: Card
    big_card: Card
    
    @validator('small_card')
    def validate_small_card(cls, v):
        """Validate that small_card is actually small."""
        if v.card_type != CardType.SMALL:
            raise ValueError("small_card must be a small card (A-6)")
        return v
    
    @validator('big_card')
    def validate_big_card(cls, v):
        """Validate that big_card is actually big."""
        if v.card_type != CardType.BIG:
            raise ValueError("big_card must be a big card (8-K)")
        return v
    
    @property
    def cost(self) -> int:
        """Cost is the rank of the small card."""
        return self.small_card.rank.value
    
    def get_pnl(self, stock_price: int) -> int:
        """
        Calculate pair value: max(big card value, 0) - cost.
        
        For red cards: max(stock_price - big_rank, 0) - cost
        For black cards: max(big_rank - stock_price, 0) - cost
        
        Args:
            stock_price: Current stock price
            
        Returns:
            int: max(big card value, 0) - cost
        """
        big_card_value = self.big_card.get_value(stock_price)
        return big_card_value - self.cost

    def get_value(self, stock_price: int) -> int:
        """Calculate pair value based on stock price."""
        return self.big_card.get_value(stock_price)
    
    def get_breakeven_price(self) -> Optional[int]:
        """Calculate breakeven price for this pair."""
        if self.big_card.rank == CardRank.SEVEN:
            return None
            
        small_rank = self.small_card.rank.value
        big_rank = self.big_card.rank.value
        
        if self.big_card.is_red:
            return big_rank + small_rank  # >= X
        else:  # black
            return big_rank - small_rank  # <= X
    
    def get_breakeven_price_str(self) -> Optional[str]:
        """Get breakeven price with >= or <= prefix."""
        price = self.get_breakeven_price()
        if price is None:
            return None
            
        if self.big_card.is_red:
            return f">={price}"
        else:  # black
            return f"<={price}"
    
    def convert_big_card_color(self) -> 'CardPair':
        """Convert the color of the big card only."""
        return CardPair(
            small_card=self.small_card,
            big_card=self.big_card.convert_color()
        ) 