"""
CardPile module for managing draw and discard piles.
"""
from typing import List, Optional, Dict
import random
from sortedcontainers import SortedList
from pydantic import BaseModel, Field
from card import Card, CardPair, CardSuit, CardRank, CardType


class CardPile(BaseModel):
    draw_pile: Dict[CardSuit, SortedList[Card]] = Field(default_factory=lambda: {
        suit: SortedList(key=lambda c: c.rank.value) for suit in CardSuit
    })
    discard_pile: List[Card] = Field(default_factory=list)
    initial_seven_cards: List[Card] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_piles()
    
    def _initialize_piles(self):
        """Initialize all card piles."""
        # Create all possible cards
        for suit in CardSuit:
            for rank in CardRank:
                if rank != CardRank.SEVEN:  # Skip seven cards
                    # Add regular cards to draw pile
                    card_type = CardType.SMALL if rank.value <= 6 else CardType.BIG
                    card = Card(suit=suit, rank=rank, card_type=card_type)
                    self.draw_pile[suit].add(card)

        # Save initial seven cards, directly create cards
        self.initial_seven_cards = [Card(suit=suit, rank=CardRank.SEVEN, card_type=CardType.SPECIAL) for suit in CardSuit]

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
            Optional[CardPair]: A card pair if available, None if draw pile is empty
        """
        # Find a suit with both small and big cards
        for suit, cards in self.draw_pile.items():
            small_cards = [c for c in cards if c.card_type == CardType.SMALL]
            big_cards = [c for c in cards if c.card_type == CardType.BIG]
            
            if small_cards and big_cards:
                # Draw one of each
                small_card = small_cards[0]
                big_card = big_cards[0]
                cards.remove(small_card)
                cards.remove(big_card)
                return CardPair(small_card=small_card, big_card=big_card)
        
        return None
    
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
        return sum(len(cards) for cards in self.draw_pile.values())
    
    @property
    def discard_pile_size(self) -> int:
        """Get number of cards in discard pile."""
        return len(self.discard_pile)
    
    def get_draw_pile(self) -> Dict[CardSuit, List[Card]]:
        """Get copy of draw pile."""
        return {suit: cards.copy() for suit, cards in self.draw_pile.items()}
    
    def get_discard_pile(self) -> List[Card]:
        """Get copy of discard pile."""
        return self.discard_pile.copy()

    def get_draw_pile_size(self) -> int:
        """Get size of draw pile."""
        return sum(len(cards) for cards in self.draw_pile.values())