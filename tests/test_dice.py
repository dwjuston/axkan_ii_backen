"""
Unit tests for dice functionality.
"""
import pytest
from unittest.mock import patch
from dice import (
    Dice,
    DiceCollectionType,
    create_dice_collection,
    roll_collection
)

def test_dice_creation():
    """Test basic dice creation."""
    positive_dice = Dice(is_positive=True)
    negative_dice = Dice(is_positive=False)
    
    assert positive_dice.is_positive is True
    assert negative_dice.is_positive is False
    assert positive_dice.current_value == 0
    assert negative_dice.current_value == 0

def test_dice_roll():
    """Test dice rolling with mocked random values."""
    with patch('random.randint') as mock_randint:
        mock_randint.return_value = 4
        dice = Dice(is_positive=True)
        value = dice.roll()
        
        assert value == 4
        assert dice.current_value == 4
        mock_randint.assert_called_once_with(1, 6)

def test_create_dice_collection():
    """Test creation of different dice collections."""
    # Test regular collection
    regular = create_dice_collection(DiceCollectionType.REGULAR)
    assert len(regular) == 2
    assert regular[0].is_positive is True
    assert regular[1].is_positive is False
    
    # Test inflation collection
    inflation = create_dice_collection(DiceCollectionType.INFLATION)
    assert len(inflation) == 3
    assert inflation[0].is_positive is True
    assert inflation[1].is_positive is True
    assert inflation[2].is_positive is False
    
    # Test tapering collection
    tapering = create_dice_collection(DiceCollectionType.TAPERING)
    assert len(tapering) == 3
    assert tapering[0].is_positive is True
    assert tapering[1].is_positive is False
    assert tapering[2].is_positive is False
    
    # Test stimulus collection
    stimulus = create_dice_collection(DiceCollectionType.STIMULUS)
    assert len(stimulus) == 1
    assert stimulus[0].is_positive is True
    
    # Test tariff collection
    tariff = create_dice_collection(DiceCollectionType.TARIFF)
    assert len(tariff) == 1
    assert tariff[0].is_positive is False
    
    # Test bullish collection
    bullish = create_dice_collection(DiceCollectionType.SOFT_LANDING)
    assert len(bullish) == 2
    assert bullish[0].is_positive is True
    assert bullish[1].is_positive is False
    
    # Test bearish collection
    bearish = create_dice_collection(DiceCollectionType.SUPPLY_SHOCK)
    assert len(bearish) == 2
    assert bearish[0].is_positive is True
    assert bearish[1].is_positive is False

def test_roll_collection():
    """Test rolling collections with mocked random values."""
    with patch('random.randint') as mock_randint:
        mock_randint.return_value = 4
        
        # Test regular collection
        total, values, extra = roll_collection(DiceCollectionType.REGULAR)
        assert values == [4, -4]
        assert total == 0  # 4 - 4 = 0
        assert extra == 0
        
        # Test inflation collection
        total, values, extra = roll_collection(DiceCollectionType.INFLATION)
        assert values == [4, 4, -4]
        assert total == 4  # 4 + 4 - 4 = 4
        
        # Test tapering collection
        total, values, extra = roll_collection(DiceCollectionType.TAPERING)
        assert values == [4, -4, -4]
        assert total == -4  # 4 - 4 - 4 = -4
        
        # Test stimulus collection
        total, values, extra = roll_collection(DiceCollectionType.STIMULUS)
        assert values == [4]
        assert total == 4
        
        # Test tariff collection
        total, values, extra = roll_collection(DiceCollectionType.TARIFF)
        assert values == [-4]
        assert total == -4
        
        # Test bullish collection
        total, values, extra = roll_collection(DiceCollectionType.SOFT_LANDING)
        assert values == [4, -4]
        assert total == 1  # (4 - 4) + 1 = 1
        
        # Test bearish collection
        total, values, extra = roll_collection(DiceCollectionType.SUPPLY_SHOCK
                                               )
        assert values == [4, -4]
        assert total == -1  # (4 - 4) - 1 = -1

def test_invalid_collection_type():
    """Test handling of invalid collection type."""
    with pytest.raises(ValueError):
        create_dice_collection("INVALID_TYPE")  # type: ignore 