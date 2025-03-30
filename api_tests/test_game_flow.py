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

def test_game_flow_to_turn_7(game_in_progress):
    """Test game flow from initial dice roll to turn 7"""
    game_id, player1_id, player2_id = game_in_progress

    # Roll initial dice as player 1
    roll_response = client.post(f"/api/v1/games/{game_id}/moves", json={"player_id": player1_id, "move_type": "roll_dice", "move_data": {}})
    assert roll_response.status_code == 200

    # Play 7 turns
    for turn in range(1, 8):
        # First player selects
        select_response1 = client.post(f"/api/v1/games/{game_id}/moves", 
            json={"player_id": player1_id,
                  "move_type": "select_pair",
                  "move_data": {"pair_index": 0}})
        assert select_response1.status_code == 200
        select_data1 = select_response1.json()
        assert select_data1["status"] == "success"
        assert select_data1["message"] == "Pair selected"

        # Second player selects
        select_response2 = client.post(f"/api/v1/games/{game_id}/moves", 
            json={"player_id": player2_id,
                  "move_type": "select_pair",
                  "move_data": {"pair_index": 0}})
        assert select_response2.status_code == 200
        select_data2 = select_response2.json()
        assert select_data2["status"] == "success"
        assert select_data2["message"] == "Pair selected"

        # Get board data for player 1, the selected pairs should be 1 at turn 1, 2 at turn 2, and so on
        board_response1 = client.get(f"/api/v1/games/{game_id}/state?player_id={player1_id}")
        assert board_response1.status_code == 200
        board_data1 = board_response1.json()
        assert board_data1["status"] == "success"
        assert len(board_data1["data"]["current_player"]["portfolio"]["regular_pairs"]) == turn
        assert len(board_data1["data"]["available_pairs"]) == 1
        assert board_data1["data"]["current_player"]["current_score"] is not None
        assert board_data1["data"]["opponent"]["current_score"] is not None

        # Get board data for player 2, check its current score is not none
        board_response2 = client.get(f"/api/v1/games/{game_id}/state?player_id={player2_id}")
        assert board_response2.status_code == 200
        board_data2 = board_response2.json()
        assert board_data2["status"] == "success"
        assert len(board_data2["data"]["current_player"]["portfolio"]["regular_pairs"]) == turn
        assert board_data2["data"]["current_player"]["current_score"] is not None
        assert board_data2["data"]["opponent"]["current_score"] is not None

        # Roll dice
        roll_response = client.post(f"/api/v1/games/{game_id}/moves", 
            json={"player_id": player1_id, "move_type": "roll_dice", "move_data": {}})
        assert roll_response.status_code == 200
        roll_data = roll_response.json()
        assert roll_data["status"] == "success"
        assert roll_data["message"] == "Dice rolled"

    # in the end, we should reach final review phase
    board_response1 = client.get(f"/api/v1/games/{game_id}/state?player_id={player1_id}")
    assert board_response1.status_code == 200
    board_data1 = board_response1.json()
    assert board_data1["status"] == "success"
    assert board_data1["data"]["current_phase"] == "final_review"

    # Both players end review and calculate final scores and winner
    end_review_response1 = client.post(f"/api/v1/games/{game_id}/moves",
        json={"player_id": player1_id, "move_type": "end_review", "move_data": {}})
    assert end_review_response1.status_code == 200
    end_review_data1 = end_review_response1.json()
    assert end_review_data1["status"] == "success"
    assert end_review_data1["message"] == "Review ended"

    end_review_response2 = client.post(f"/api/v1/games/{game_id}/moves",
        json={"player_id": player2_id, "move_type": "end_review", "move_data": {}})
    assert end_review_response2.status_code == 200
    end_review_data2 = end_review_response2.json()
    assert end_review_data2["status"] == "success"
    assert end_review_data2["message"] == "Review ended"

    # Get final game state
    """
    @router.get("/games/{game_id}/results", response_model=GameResponse)
    async def get_game_results(game_id: str):
    """
    results_response = client.get(f"/api/v1/games/{game_id}/results")
    assert results_response.status_code == 200
    results_data = results_response.json()
    assert results_data["status"] == "success"
    assert results_data["message"] == "Game results retrieved successfully"
    assert results_data["data"]["winner"] is not None
    assert results_data["data"][player1_id] is not None
    assert results_data["data"][player2_id] is not None
