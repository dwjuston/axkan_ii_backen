import pytest
from fastapi.testclient import TestClient
from api import app
from api.models import GameResponse
from api.routes import game_sessions, game_players

@pytest.fixture(autouse=True)
def clear_game_state():
    """Clear game state before each test"""
    game_sessions.clear()
    game_players.clear()
    yield

client = TestClient(app)

def test_create_new_game():
    """Test creating a new game as first player"""
    response = client.post("/api/v1/games", json={"player_name": "Player1"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Created new game"
    assert "game_id" in data["data"]
    assert "player_id" in data["data"]
    assert data["data"]["is_first_player"] is True

def test_join_existing_game():
    """Test joining an existing game as second player"""
    # First create a game
    create_response = client.post("/api/v1/games", json={"player_name": "Player1"})
    assert create_response.status_code == 200
    game_id = create_response.json()["data"]["game_id"]
    
    # Then join it as second player
    join_response = client.post("/api/v1/games", json={"player_name": "Player2"})
    assert join_response.status_code == 200
    data = join_response.json()
    assert data["status"] == "success"
    assert data["message"] == "Joined existing game"
    assert data["data"]["game_id"] == game_id
    assert "player_id" in data["data"]
    assert data["data"]["is_first_player"] is False

def test_websocket_connection():
    """Test WebSocket connection establishment"""
    # First create a game
    create_response = client.post("/api/v1/games", json={"player_name": "Player1"})
    assert create_response.status_code == 200
    game_data = create_response.json()["data"]
    game_id = game_data["game_id"]
    player_id = game_data["player_id"]
    
    # Test WebSocket connection with player_id
    with client.websocket_connect(f"/api/v1/games/{game_id}/ws?player_id={player_id}") as websocket:
        # Send a test message to verify connection
        websocket.send_text("test")
        # If no exception is raised, the connection was successful 