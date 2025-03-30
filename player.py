"""
Player class for managing player state and actions.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

from card import Card, CardPair
from portfolio import Portfolio


class Player(BaseModel):
    player_id: str
    portfolio: Portfolio = Field(default_factory=Portfolio)
    has_selected: bool = False  # Track if player has made their selection for current turn
    current_score: int = 0  # Track player's current score

    @property
    def cost(self) -> int:
        """Get total cost of selected pairs."""
        return self.portfolio.get_total_cost()

    @property
    def selected_pairs(self) -> List[CardPair]:
        """Get list of selected pairs."""
        return self.portfolio.get_selected_pairs()
    
    @property
    def seven_cards(self) -> List[Card]:
        """Get list of seven cards."""
        return self.portfolio.get_seven_cards()
    
    @property
    def hidden_pairs(self) -> List[CardPair]:
        """Get list of hidden pairs."""
        return self.portfolio.get_hidden_pairs()
    
    def select_pair(self, pair: CardPair) -> bool:
        """
        Select a pair for the current turn.
        
        Args:
            pair: The card pair to select
            
        Returns:
            bool: True if selection was successful, False otherwise
        """
        if not self.is_valid_selection(pair):
            return False
        self.portfolio.add_pair(pair)
        self.has_selected = True
        return True
    
    def use_seven_card(self, special_card: Card) -> Optional[Card]:
        """
        Use a seven card for special actions.
        
        Returns:
            Optional[Card]: The seven card if available, None otherwise
        """
        if not self.portfolio.has_seven_card():
            return None
        return self.portfolio.use_seven_card(special_card)
    
    def convert_card_color(self, pair: CardPair, special_card_index: int) -> bool:
        """
        Convert color of a card using seven card.
        
        Args:
            pair: The card pair to convert
            special_card_index: Index of the special card
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """

        special_card = self.seven_cards[special_card_index]

        # Find the pair in the portfolio
        pairs = self.portfolio.get_selected_pairs()
        for i, p in enumerate(pairs):
            if p == pair:
                self.portfolio.convert_pair_color(i)
                self.portfolio.use_seven_card(special_card)
                return True
                
        # Check hidden pair
        hidden_pairs = self.portfolio.get_hidden_pairs()
        if hidden_pairs and hidden_pairs[0] == pair:
            self.portfolio.convert_pair_color(-1)  # -1 for hidden pair
            self.portfolio.use_seven_card(special_card)
            return True
            
        return False
    
    def get_pnl(self, stock_price: int) -> int:
        """Get player's PnL."""
        return self.portfolio.get_pnl(stock_price)
    
    def is_valid_selection(self, pair: CardPair) -> bool:
        """
        Validate if pair selection is valid.
        
        Args:
            pair: The card pair to validate
            
        Returns:
            bool: True if selection is valid, False otherwise
        """
        return pair is not None and not self.has_selected
    
    def reset_turn_state(self):
        """Reset player's state for the next turn."""
        self.has_selected = False 
    
    def recalculate_score(self, stock_price: int) -> None:
        """
        Recalculate player's score based on current stock price.
        
        Args:
            stock_price: Current stock price
        """
        self.current_score = self.portfolio.get_pnl(stock_price) 