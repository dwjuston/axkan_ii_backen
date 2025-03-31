from typing import Protocol
from venv import logger

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
    # logging
    logger.info(f"broadcaster - broadcast_notification: {notification}")
    
    # Convert notification to JSON string once
    notification_json = notification.model_dump_json()
    
    if notification.target_players:
        # Send to specific players
        for player_id in notification.target_players:
            logger.info(f"broadcaster - broadcast_notification: Sending to player {player_id}")
            await websocket_manager.send_to_player(
                notification.game_id,
                player_id,
                notification_json
            )
    else:
        # Broadcast to all players in the game
        logger.info(f"broadcaster - broadcast_notification: Broadcasting to all players in game {notification.game_id}")
        await websocket_manager.broadcast_to_game(
            notification.game_id,
            notification_json
        ) 