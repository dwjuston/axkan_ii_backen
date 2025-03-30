import pytest
from fastapi.testclient import TestClient
from api import app
from api.models import GameResponse, GameMove
from api.routes import game_sessions, game_players

@pytest.fixture(autouse=True)
def clear_game_state():
    """Clear game state before each test"""
    game_sessions.clear()
    game_players.clear()
    yield

# create fixture to mock game already in progress
@pytest.fixture
def game_in_progress():
    """Create a game with two players and return game_id"""
    # Create first player and game
    create_response = client.post("/api/v1/games", json={"player_name": "Player1"})
    data1 = create_response.json()
    assert data1["status"] == "success"
    game_id = data1["data"]["game_id"]
    player1_id = data1["data"]["player_id"]

    # Join as second player
    join_response = client.post("/api/v1/games", json={"player_name": "Player2"})
    assert join_response.status_code == 200
    data2 = join_response.json()
    assert data2["status"] == "success"
    player2_id = data2["data"]["player_id"]

    return game_id, player1_id, player2_id

client = TestClient(app)


def test_get_board_data(game_in_progress):
    """Test getting board data for both players"""
    game_id, player1_id, player2_id = game_in_progress

    # Get board data for player 1
    board_response1 = client.get(f"/api/v1/games/{game_id}/state?player_id={player1_id}")
    assert board_response1.status_code == 200
    board_data1 = board_response1.json()
    assert board_data1["status"] == "success"
    
    # Verify player 1's board data
    data1 = board_data1["data"]
    assert data1["stock_price"] is None  # Initial state
    assert data1["turn_number"] == 1
    assert len(data1["available_pairs"]) == 0  # No pairs available yet
    assert len(data1["selected_pairs"]) == 0  # No pairs selected yet
    assert data1["current_player"]["player_id"] == player1_id
    assert data1["opponent"]["player_id"] == player2_id
    assert len(data1["current_player"]["portfolio"]["seven_cards"]) == 2  # Two seven cards
    assert data1["current_player"]["portfolio"]["hidden_pair"] is not None  # One hidden pair
    assert data1["opponent"]["portfolio"]["hidden_pair"] is None  # Opponent's hidden pairs not visible
    
    # Get board data for player 2
    board_response2 = client.get(f"/api/v1/games/{game_id}/state?player_id={player2_id}")
    assert board_response2.status_code == 200
    board_data2 = board_response2.json()
    assert board_data2["status"] == "success"
    
    # Verify player 2's board data
    data2 = board_data2["data"]
    assert data2["stock_price"] is None  # Initial state
    assert data2["turn_number"] == 1
    assert len(data2["available_pairs"]) == 0  # No pairs available yet
    assert len(data2["selected_pairs"]) == 0  # No pairs selected yet
    assert data2["current_player"]["player_id"] == player2_id
    assert data2["opponent"]["player_id"] == player1_id
    assert len(data2["current_player"]["portfolio"]["seven_cards"]) == 2  # Two seven cards
    assert data2["current_player"]["portfolio"]["hidden_pair"] is not None  # One hidden pair
    assert data2["opponent"]["portfolio"]["hidden_pair"] is None  # Opponent's hidden pairs not visible

def test_initial_dice_roll(game_in_progress):
    """Test initial dice roll and game state after roll"""
    game_id, player1_id, player2_id = game_in_progress

    # Roll initial dice as player 1
    roll_response = client.post(f"/api/v1/games/{game_id}/moves", json={"player_id": player1_id, "move_type": "roll_dice", "move_data": {}})
    assert roll_response.status_code == 200
    roll_data = roll_response.json()
    assert roll_data["status"] == "success"
    assert roll_data["message"] == "Dice rolled"

    # Verify game state after roll
    state_response = client.get(f"/api/v1/games/{game_id}/state?player_id={player1_id}")
    assert state_response.status_code == 200
    state_data = state_response.json()
    assert state_data["status"] == "success"
    assert state_data["data"]["stock_price"] is not None  # Stock price set
    assert state_data["data"]["turn_number"] == 1
    assert len(state_data["data"]["available_pairs"]) == 3  # 6 pairs available
    assert len(state_data["data"]["selected_pairs"]) == 0  # No pairs selected yet
    assert state_data["data"]["current_player"]["player_id"] == player1_id
    assert state_data["data"]["opponent"]["player_id"] == player2_id