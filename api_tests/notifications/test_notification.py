import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from notifications.models import Notification, NotificationType
from notifications.broadcaster import broadcast_notification

class MockWebSocketManager:
    async def send_to_player(self, game_id: str, player_id: str, message: str):
        pass
        
    async def broadcast_to_game(self, game_id: str, message: str):
        pass

def test_notification_model():
    # Test creation with required fields
    notification = Notification(
        type=NotificationType.GAME_STARTED,
        data={"current_turn": 1},
        game_id="test_game"
    )
    assert notification.type == NotificationType.GAME_STARTED
    assert notification.game_id == "test_game"
    assert notification.timestamp is not None
    assert notification.target_players is None
    
    # Test with target players
    notification = Notification(
        type=NotificationType.PLAYER_TURN,
        data={"player_id": "123"},
        game_id="test_game",
        target_players=["123", "456"]
    )
    assert notification.target_players == ["123", "456"]
    
    # Test data validation
    with pytest.raises(ValueError):
        Notification(
            type="invalid_type",  # Should be NotificationType
            data={"player_id": "123"},
            game_id="test_game"
        )

@pytest.mark.asyncio
async def test_broadcast_notification():
    # Create mock WebSocket manager
    mock_ws_manager = AsyncMock(spec=MockWebSocketManager)
    
    # Test broadcasting to all players
    notification = Notification(
        type=NotificationType.GAME_STARTED,
        data={"current_turn": 1},
        game_id="test_game"
    )
    await broadcast_notification(notification, mock_ws_manager)
    mock_ws_manager.broadcast_to_game.assert_called_once_with(
        "test_game",
        notification.model_dump_json()
    )
    
    # Reset mock
    mock_ws_manager.reset_mock()
    
    # Test sending to specific players
    notification = Notification(
        type=NotificationType.PLAYER_TURN,
        data={"player_id": "123"},
        game_id="test_game",
        target_players=["123", "456"]
    )
    await broadcast_notification(notification, mock_ws_manager)
    assert mock_ws_manager.send_to_player.call_count == 2
    mock_ws_manager.send_to_player.assert_any_call(
        "test_game",
        "123",
        notification.model_dump_json()
    )
    mock_ws_manager.send_to_player.assert_any_call(
        "test_game",
        "456",
        notification.model_dump_json()
    ) 