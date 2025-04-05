"""
Player class for managing player state and actions.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

from card import Card, CardPair
from portfolio import Portfolio


class OpponentView(BaseModel):
    uuid: str
    name: str
    player_id: int
    selected_pairs: List[CardPair]
    seven_cards: List[Card]
    pnl: int
    cost: int
    value: int

class PlayerView(BaseModel):
    uuid: str
    player_id: int
    name: str
    selected_pairs: List[CardPair]
    seven_cards: List[Card]
    hidden_pair: Optional[CardPair]
    pnl: int
    cost: int
    value: int

class Player(BaseModel):
    uuid: str = Field(default_factory=str)
    player_id: int = Field(default_factory=int)
    name: str = Field(default_factory=str)
    portfolio: Portfolio = Field(default_factory=Portfolio)

    @property
    def selected_pairs(self) -> List[CardPair]:
        """Get list of selected pairs."""
        return self.portfolio.regular_pairs
    
    @property
    def seven_cards(self) -> List[Card]:
        """Get list of seven cards."""
        return self.portfolio.seven_cards
    
    @property
    def hidden_pair(self) -> Optional[CardPair]:
        """Get list of hidden pairs."""
        return self.portfolio.hidden_pairs[0] if len(self.portfolio.hidden_pairs) > 0 else None
    
    def select_pair(self, pair: CardPair) -> None:
        self.portfolio.add_pair(pair)
    
    def remove_seven_card(self, special_card: Card) -> None:
        self.portfolio.remove_seven_card(special_card)
    
    def convert_card_color(self, pair: CardPair, special_card_index: int) -> bool:
        special_card = self.seven_cards[special_card_index]
        # Find the pair in the portfolio
        pairs = self.portfolio.regular_pairs
        for i, p in enumerate(pairs):
            if p == pair:
                self.portfolio.convert_pair_color(i)
                self.portfolio.remove_seven_card(special_card)
                return True
                
        # Check hidden pair
        hidden_pairs = self.portfolio.hidden_pairs
        if pair in hidden_pairs:
            self.portfolio.convert_pair_color(-1)  # -1 for hidden pair
            self.portfolio.remove_seven_card(special_card)
            return True
            
        return False
    
    def get_pnl(self, stock_price: int, include_hidden: bool = True) -> int:
        """Get player's PnL."""
        return self.portfolio.get_pnl(stock_price, include_hidden)

    def get_cost(self, include_hidden: bool = True) -> int:
        """Get player's total cost."""
        return self.portfolio.get_cost(include_hidden)

    def get_value(self, stock_price: int, include_hidden: bool = True) -> int:
        """Get player's total value."""
        return self.portfolio.get_value(stock_price, include_hidden)

    def get_player_view(self, stock_price: Optional[int]) -> PlayerView:
        """Get player's view."""
        return PlayerView(
            uuid=self.uuid,
            player_id=self.player_id,
            name=self.name,
            selected_pairs=self.selected_pairs,
            seven_cards=self.seven_cards,
            hidden_pair=self.hidden_pair,
            pnl=self.get_pnl(stock_price) if stock_price else 0,
            cost=self.get_cost(),
            value=self.get_value(stock_price) if stock_price else 0
        )

    def get_opponent_view(self, stock_price: Optional[int]) -> OpponentView:
        """Get player's view."""
        return OpponentView(
            uuid=self.uuid,
            name=self.name,
            player_id=self.player_id,
            selected_pairs=self.selected_pairs,
            seven_cards=self.seven_cards,
            pnl=self.get_pnl(stock_price, False) if stock_price else 0,
            cost=self.get_cost(False),
            value=self.get_value(stock_price, False) if stock_price else 0
        )