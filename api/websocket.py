from fastapi import WebSocket
from typing import Dict, List
from game_manager import GameManager

class WebSocketManager:
    def __init__(self):
        # Store active connections per game
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, game_id: str):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                
    async def broadcast_to_game(self, game_id: str, message: dict):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_json(message)

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 