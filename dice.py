"""
Dice module for handling individual dice and dice collections.
"""
import random
from enum import Enum, auto
from typing import List, Tuple

class DiceCollectionType(Enum):
    """Types of dice collections available in the game."""
    INITIAL = auto()      # 1 positive
    REGULAR = auto()      # 1 positive, 1 negative
    INFLATION = auto()    # 2 positive, 1 negative
    TAPERING = auto()     # 1 positive, 2 negative
    STIMULUS = auto()     # 1 positive
    TARIFF = auto()       # 1 negative
    BULLISH = auto()      # 1 positive, 1 negative, result +1
    BEARISH = auto()      # 1 positive, 1 negative, result -1

class Dice:
    """Represents a single die that can be positive or negative."""
    
    def __init__(self, is_positive: bool):
        """
        Initialize a die.
        
        Args:
            is_positive: True for positive die, False for negative die
        """
        self.is_positive = is_positive
        self.current_value = 0
    
    def roll(self) -> int:
        """
        Roll the die and return a random value between 1 and 6.
        
        Returns:
            int: Random value between 1 and 6
        """
        self.current_value = random.randint(1, 6)
        return self.current_value
    
    def __str__(self) -> str:
        """String representation of the die."""
        sign = "+" if self.is_positive else "-"
        return f"{sign}{self.current_value}"

def create_dice_collection(collection_type: DiceCollectionType) -> List[Dice]:
    """
    Creates a list of dice based on collection type, positive dice first.
    
    Args:
        collection_type: Type of dice collection to create
        
    Returns:
        List[Dice]: List of dice in the collection
        
    Raises:
        ValueError: If collection_type is unknown
    """
    if collection_type == DiceCollectionType.REGULAR:
        return [Dice(is_positive=True), Dice(is_positive=False)]
    elif collection_type == DiceCollectionType.INFLATION:
        return [Dice(is_positive=True), Dice(is_positive=True), Dice(is_positive=False)]
    elif collection_type == DiceCollectionType.TAPERING:
        return [Dice(is_positive=True), Dice(is_positive=False), Dice(is_positive=False)]
    elif collection_type == DiceCollectionType.STIMULUS:
        return [Dice(is_positive=True)]
    elif collection_type == DiceCollectionType.TARIFF:
        return [Dice(is_positive=False)]
    elif collection_type in (DiceCollectionType.BULLISH, DiceCollectionType.BEARISH):
        return [Dice(is_positive=True), Dice(is_positive=False)]
    elif collection_type == DiceCollectionType.INITIAL:
        return [Dice(is_positive=True)]
    raise ValueError(f"Unknown collection type: {collection_type}")

def roll_collection(collection_type: DiceCollectionType) -> Tuple[List[int], int]:
    """
    Roll all dice and return list of values and total sum.
    
    Args:
        dice_list: List of dice to roll
        collection_type: Type of dice collection
        
    Returns:
        Tuple[List[int], int]: (list of values, total sum)
    """
    dice_list = create_dice_collection(collection_type)
    values = [dice.roll() for dice in dice_list]
    
    # Calculate base sum
    total = sum(value if dice.is_positive else -value 
                for value, dice in zip(values, dice_list))
    
    # Apply special modifiers
    if collection_type == DiceCollectionType.BULLISH:
        total += 1
    elif collection_type == DiceCollectionType.BEARISH:
        total -= 1
        
    return values, total 