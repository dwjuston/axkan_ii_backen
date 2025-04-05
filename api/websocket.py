import json
from dataclasses import dataclass
from venv import logger

from fastapi import WebSocket
from typing import Dict, List, Optional
from asyncio import Queue

@dataclass
class WebSocketMessage:
    game_id: str
    player_uuids: Optional[list[str]]  # Optional because broadcast messages might not target specific players
    text: str

class WebSocketManager:
    def __init__(self):
        # Store active connections per game
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {} # game_id -> player_uuid -> WebSocket
        
    async def connect(self, websocket: WebSocket, game_id: str, player_uuid: str):
        """Connect a WebSocket and store it with its game_id."""
        # check if reconnecting
        if game_id in self.active_connections and player_uuid in self.active_connections[game_id]:
            old_ws = self.active_connections[game_id][player_uuid]
            try:
                await old_ws.close()
            except Exception as e:
                pass

        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}

        self.active_connections[game_id][player_uuid] = websocket
        # Accept the connection
        await websocket.accept()

    async def reconnect(self, websocket: WebSocket, game_id: str, player_uuid: str):
        old_ws = self.active_connections[game_id][player_uuid]
        try:
            await old_ws.close()
        except Exception as e:
            pass
        self.active_connections[game_id][player_uuid] = websocket
        await websocket.accept()
        
    async def disconnect(self, websocket: WebSocket, game_id: str, player_uuid: str):
        """Disconnect a WebSocket and remove it from storage."""

        if game_id in self.active_connections:
            ws = self.active_connections[game_id].pop(player_uuid)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
            try:
                await ws.close()
            except Exception as e:
                pass

    async def send(self, game_id: str, player_uuids: Optional[list[str]], message_type: str, message: str):
        """Broadcast a message to all connections in a game."""
        if player_uuids is None:
            if game_id in self.active_connections:
                for connection in self.active_connections[game_id].values():
                    try:
                        await connection.send_json({
                            "type": message_type,
                            "content": message})
                    except:
                        raise Exception("Error sending message")
        else:
            if game_id in self.active_connections:
                for player_uuid in player_uuids:
                    if player_uuid in self.active_connections[game_id]:
                        connection = self.active_connections[game_id][player_uuid]
                        try:
                            await connection.send_json({
                                "type": message_type,
                                "content": message})
                        except Exception as e:
                            raise Exception("Error sending message")

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
