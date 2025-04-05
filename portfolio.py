"""
Portfolio module for managing a player's selected card pairs and calculating portfolio metrics.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from card import Card, CardPair

class Portfolio(BaseModel):
    regular_pairs: List[CardPair] = Field(default_factory=list)  # Pairs selected during turns
    hidden_pairs: List[CardPair] = Field(default_factory=list)  # Hidden pair selected during turn 7
    seven_cards: List[Card] = Field(default_factory=list)  # Seven cards for special actions

    def get_cost(self, include_hidden: bool = True) -> int:
        """Calculate total cost of all pairs."""
        cost = sum([pair.cost for pair in self.regular_pairs])
        if include_hidden:
            return cost + sum([pair.cost for pair in self.hidden_pairs])
        return cost
        
    def get_value(self, stock_price: int, include_hidden: bool = True) -> int:
        """Calculate total value based on given stock price."""
        value = sum([pair.get_value(stock_price) for pair in self.regular_pairs])
        if include_hidden:
            return value + sum([pair.get_value(stock_price) for pair in self.hidden_pairs])
        return value
        
    def get_pnl(self, stock_price: int, include_hidden: bool = True) -> int:
        """Calculate profit and loss (total value - total cost)."""
        return self.get_value(stock_price, include_hidden) - self.get_cost(include_hidden)
        
    def add_pair(self, pair: CardPair) -> None:
        """Add a regular pair to the portfolio."""
        self.regular_pairs.append(pair)
            
    def add_hidden_pair(self, pair: CardPair) -> None:
        """Add a hidden pair to the portfolio."""
        self.hidden_pairs.append(pair)

        
    def add_seven_card(self, card: Card) -> None:
        """Add a seven card to the portfolio."""
        if card.rank.value != 7:
            raise ValueError("Card must be a seven card")
        self.seven_cards.append(card)
            
    def remove_seven_card(self, special_card: Card) -> None:
        """Use and remove a seven card if available."""
        flag = False
        for card in self.seven_cards:
            if card == special_card:
                self.seven_cards.remove(card)
                flag = True
        if not flag:
            raise ValueError("Card not found in seven cards")
        
    def has_seven_card(self) -> bool:
        """Check if portfolio has any seven cards."""
        return bool(self.seven_cards)
        
    def convert_pair_color(self, pair_index: int) -> None:
        """Convert color of a specific pair (for turn 8)."""
        if 0 <= pair_index < len(self.regular_pairs):
            self.regular_pairs[pair_index] = self.regular_pairs[pair_index].convert_big_card_color()
        elif pair_index == -1 and len(self.hidden_pairs) >= 1:
            self.hidden_pairs[0] = self.hidden_pairs[0].convert_big_card_color()

    def reset(self) -> None:
        """Reset portfolio for a new game."""
        self.regular_pairs = []
        self.hidden_pairs = []
        self.seven_cards = []