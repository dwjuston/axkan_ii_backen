"""
CardPile module for managing draw and discard piles.
"""
from typing import List, Optional, Dict
import random
from sortedcontainers import SortedList
from pydantic import BaseModel, Field
from card import Card, CardPair, CardSuit, CardRank, CardType


class CardPile(BaseModel):
    small_card_draw_pile: list[Card] = Field(default_factory=list)
    big_card_draw_pile: list[Card] = Field(default_factory=list)
    discard_pile: List[Card] = Field(default_factory=list)
    initial_seven_cards: List[Card] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_piles()
    
    def _initialize_piles(self):
        """Initialize all card piles."""
        # Create all possible cards
        for suit in CardSuit:
            for rank in CardRank:
                card = Card(suit=suit, rank=rank)
                if card.card_type == CardType.SMALL:
                    self.small_card_draw_pile.append(card)
                elif card.card_type == CardType.BIG:
                    self.big_card_draw_pile.append(card)

        # Save initial seven cards, directly create cards
        self.initial_seven_cards = [Card(suit=suit, rank=CardRank.SEVEN) for suit in CardSuit]

    def draw_seven_cards(self) -> List[Card]:
        """
        Draw seven cards from the draw pile.

        Returns:
            List[Card]: List of seven cards drawn
        """
        # pop two seven cards
        seven_cards = random.sample(self.initial_seven_cards, 2)
        return seven_cards

    def draw_pair(self) -> Optional[CardPair]:
        """
        Draw a pair of cards (one big, one small).
        
        Returns:
            CardPair
        """
        # Check if draw pile is empty
        if not self.small_card_draw_pile or not self.big_card_draw_pile:
            return None

        # Find a suit with both small and big cards
        small_card_rand_idx = random.randint(0, len(self.small_card_draw_pile) - 1)
        small_card = self.small_card_draw_pile.pop(small_card_rand_idx)
        big_card_rand_idx = random.randint(0, len(self.big_card_draw_pile) - 1)
        big_card = self.big_card_draw_pile.pop(big_card_rand_idx)
        return CardPair(small_card=small_card, big_card=big_card)
    
    def discard_pair(self, pair: CardPair):
        """
        Discard a pair of cards.
        
        Args:
            pair: The card pair to discard
        """
        self.discard_pile.extend([pair.small_card, pair.big_card])
    
    def shuffle_discard_into_draw(self):
        """Shuffle discard pile back into draw pile."""
        # Add all discarded cards back to their respective suit piles
        for card in self.discard_pile:
            self.draw_pile[card.suit].add(card)
        self.discard_pile.clear()
    
    @property
    def draw_pile_size(self) -> int:
        """Get number of cards in draw pile."""
        return len(self.small_card_draw_pile) + len(self.big_card_draw_pile)
    
    @property
    def discard_pile_size(self) -> int:
        """Get number of cards in discard pile."""
        return len(self.discard_pile)

    def get_discard_pile(self) -> List[Card]:
        """Get copy of discard pile."""
        return self.discard_pile.copy()

    def get_draw_pile_size(self) -> int:
        """Get size of draw pile."""
        return sum(len(cards) for cards in self.draw_pile.values())