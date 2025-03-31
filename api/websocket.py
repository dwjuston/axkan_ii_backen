from venv import logger

from fastapi import WebSocket
from typing import Dict, List
from game_manager import GameManager

class WebSocketManager:
    def __init__(self):
        # Store active connections per game
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, game_id: str):
        """Connect a WebSocket and store it with its game_id."""
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        logger.info(f"WebSocketManager - connect: Added connection for game {game_id}")
        
    def disconnect(self, websocket: WebSocket, game_id: str):
        """Disconnect a WebSocket and remove it from storage."""
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
            logger.info(f"WebSocketManager - disconnect: Removed connection for game {game_id}")
                
    async def broadcast_to_game(self, game_id: str, message: str):
        """Broadcast a message to all connections in a game."""
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_text(message)
                    logger.info(f"WebSocketManager - broadcast_to_game: Sent message to connection in game {game_id}")
                except Exception as e:
                    logger.error(f"WebSocketManager - broadcast_to_game: Error sending message: {str(e)}")

    async def send_to_player(self, game_id: str, player_id: str, message: str):
        """Send a message to a specific player in a game."""
        logger.info(f"WebSocketManager - send_to_player: {game_id}, {player_id}, {message}")
        if game_id in self.active_connections:
            logger.info(f"WebSocketManager - send_to_player: Active connections found")
            for connection in self.active_connections[game_id]:
                # Get player_id from connection scope
                conn_player_id = connection.scope.get("player_id")
                logger.info(f"WebSocketManager - send_to_player: Checking connection for player {conn_player_id}")
                if conn_player_id == player_id:
                    try:
                        await connection.send_text(message)
                        logger.info(f"WebSocketManager - send_to_player: Sent message to player {player_id}")
                    except Exception as e:
                        logger.error(f"WebSocketManager - send_to_player: Error sending message: {str(e)}")
                    break
            else:
                logger.warning(f"WebSocketManager - send_to_player: No connection found for player {player_id}")

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 