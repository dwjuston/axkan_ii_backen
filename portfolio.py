"""
Portfolio module for managing a player's selected card pairs and calculating portfolio metrics.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from card import Card, CardPair

class Portfolio(BaseModel):
    regular_pairs: List[CardPair] = Field(default_factory=list)  # Pairs selected during turns
    hidden_pair: Optional[CardPair] = None  # Hidden pair from game start
    seven_cards: List[Card] = Field(default_factory=list)  # Seven cards for special actions
    
    @property
    def total_cost(self) -> int:
        """Calculate total cost of all pairs."""
        return sum(pair.cost for pair in self.get_all_pairs())
        
    def get_total_value(self, stock_price: int) -> int:
        """Calculate total value based on given stock price."""
        return sum(pair.get_value(stock_price) for pair in self.get_all_pairs())
        
    def get_pnl(self, stock_price: int) -> int:
        """Calculate profit and loss (total value - total cost)."""
        return self.get_total_value(stock_price) - self.total_cost
        
    def add_pair(self, pair: CardPair) -> None:
        """Add a regular pair to the portfolio."""
        self.regular_pairs.append(pair)
            
    def add_hidden_pair(self, pair: CardPair) -> None:
        """Add a hidden pair to the portfolio."""
        self.hidden_pair = pair
            
    def get_selected_pairs(self) -> List[CardPair]:
        """Get all regular (non-hidden) pairs."""
        return self.regular_pairs.copy()
        
    def get_hidden_pairs(self) -> List[CardPair]:
        """Get hidden pairs as a list."""
        return [self.hidden_pair] if self.hidden_pair else []
        
    def get_all_pairs(self) -> List[CardPair]:
        """Get all pairs including hidden pair."""
        pairs = self.regular_pairs.copy()
        if self.hidden_pair:
            pairs.append(self.hidden_pair)
        return pairs
        
    def add_seven_card(self, card: Card) -> None:
        """Add a seven card to the portfolio."""
        if card.rank.value == 7:
            self.seven_cards.append(card)
            
    def use_seven_card(self, special_card: Card) -> Optional[Card]:
        """Use and remove a seven card if available."""
        for card in self.seven_cards:
            if card == special_card:
                self.seven_cards.remove(card)
                return card
        return None
        
    def has_seven_card(self) -> bool:
        """Check if portfolio has any seven cards."""
        return bool(self.seven_cards)
        
    def get_seven_cards(self) -> List[Card]:
        """Get list of available seven cards."""
        return self.seven_cards.copy()
        
    def convert_pair_color(self, pair_index: int) -> None:
        """Convert color of a specific pair (for turn 8)."""
        if 0 <= pair_index < len(self.regular_pairs):
            self.regular_pairs[pair_index] = self.regular_pairs[pair_index].convert_big_card_color()
        elif pair_index == -1 and self.hidden_pair:
            self.hidden_pair = self.hidden_pair.convert_big_card_color()

    def get_filtered_portfolio(self) -> "Portfolio":
        """Get a filtered portfolio with hidden pair and seven cards removed."""
        return Portfolio(
            regular_pairs=self.regular_pairs,
            hidden_pair=None,  # Explicitly set hidden_pair to None
            seven_cards=self.seven_cards
        )