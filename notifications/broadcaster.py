from typing import Protocol
from .models import Notification

class WebSocketManagerProtocol(Protocol):
    async def send_to_player(self, game_id: str, player_id: str, message: str) -> None:
        ...
    
    async def broadcast_to_game(self, game_id: str, message: str) -> None:
        ...

async def broadcast_notification(
    notification: Notification,
    websocket_manager: WebSocketManagerProtocol
) -> None:
    """
    Broadcast a notification to all players in a game or specific players.
    
    Args:
        notification: The notification to send
        websocket_manager: The WebSocket manager instance
    """
    if notification.target_players:
        # Send to specific players
        for player_id in notification.target_players:
            await websocket_manager.send_to_player(
                notification.game_id,
                player_id,
                notification.model_dump_json()  # Using model_dump_json instead of json()
            )
    else:
        # Broadcast to all players in the game
        await websocket_manager.broadcast_to_game(
            notification.game_id,
            notification.model_dump_json()  # Using model_dump_json instead of json()
        ) 