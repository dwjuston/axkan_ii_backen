import pytest
import asyncio
import websockets
import json
import requests
from fastapi.testclient import TestClient
from api import app

@pytest.mark.asyncio
async def test_websocket_echo():
    # Create a test client
    client = TestClient(app)
    # Get the base URL from the test client
    base_url = client.base_url
    # Create a game first
    response = client.post(f'{base_url}/api/v1/games/join', json={"player_name": "TestPlayer"})
    assert response.status_code == 200
    game_data = response.json()
    game_id = game_data['game_id']
    player_uuid = game_data['player_uuid']
    

    
    # Connect to WebSocket using the test client's base URL
    uri = f"{base_url}/games/ws?game_id={game_id}&player_uuid={player_uuid}"
    # Replace http with ws in the URL
    uri = uri.replace('http://', 'ws://')

    async with websockets.connect(uri) as websocket:
        # Send a test message
        test_message = {"type": "test", "message": "Hello WebSocket!"}
        await websocket.send(json.dumps(test_message))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify the response
        assert response_data["type"] == "test"
        assert response_data["message"] == "Hello WebSocket!" 