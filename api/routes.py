from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import uuid

from enums import GameAction, GamePhase
from game_manager import GameManager
from .models import JoinGameRequest, GameMove, GameMetadata, GameResponse, GameError
from .websocket import websocket_manager
from player import Player

router = APIRouter()

# In-memory storage for game sessions
game_sessions: Dict[str, GameManager] = {}
# Track which players have joined each game
game_players: Dict[str, Dict[str, Player]] = {}

@router.post("/games", response_model=GameResponse)
async def create_or_join_game(request: JoinGameRequest):
    """
    Create a new game or join an existing one.
    If this is the first player, creates a new game.
    If this is the second player, starts the game.
    """
    # Find an available game with one player
    available_game_id = None
    for game_id, players in game_players.items():
        if len(players) == 1:
            available_game_id = game_id
            break
    
    if available_game_id:
        # Join existing game
        game_id = available_game_id
        player_id = str(uuid.uuid4())
        
        # Create second player
        player2 = Player(player_id=player_id)
        game_players[game_id][player_id] = player2
        
        # Start the game
        game_manager = game_sessions[game_id]
        game_manager.add_player(player2)
        game_manager.start_game()

        # Initialize game
        game_manager.initialize_game()
        
        return GameResponse(
            status="success",
            message="Joined existing game",
            data={
                "game_id": game_id,
                "player_id": player_id,
                "is_first_player": False
            }
        )
    else:
        # Create new game
        game_id = str(uuid.uuid4())
        player_id = str(uuid.uuid4())
        
        # Create first player
        player1 = Player(player_id=player_id)
        
        # Initialize game manager
        game_manager = GameManager()
        game_manager.add_player(player1)
        game_sessions[game_id] = game_manager
        
        # Track players
        game_players[game_id] = {player_id: player1}
        
        return GameResponse(
            status="success",
            message="Created new game",
            data={
                "game_id": game_id,
                "player_id": player_id,
                "is_first_player": True
            }
        )

@router.websocket("/games/{game_id}/ws")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket_manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, game_id)

@router.get("/games/{game_id}/metadata", response_model=GameMetadata)
async def get_game_metadata(game_id: str):
    """
    Get game metadata including:
    - Game status (waiting/active/ended)
    - Player names
    - Current turn
    - Current phase
    """
    # TODO: Implement metadata retrieval
    # 1. Check if game exists
    # 2. Return game metadata without sensitive game state
    pass

# get final results
@router.get("/games/{game_id}/results", response_model=GameResponse)
async def get_game_results(game_id: str):
    """
    Get final game results including:
    - Player scores
    - Winner
    - Stock Price
    - Selected Pairs
    - Hidden Pair
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Get game manager
    game_manager = game_sessions[game_id]

    # Check if game has ended
    if game_manager.context.current_phase != GamePhase.GAME_END:
        raise HTTPException(status_code=400, detail="Game is not over yet")

    # Calculate final scores
    result_dict = game_manager.calculate_final_results()

    return GameResponse(
        status="success",
        message="Game results retrieved successfully",
        data=result_dict
    )

@router.post("/games/{game_id}/moves", response_model=GameResponse)
async def make_game_move(game_id: str, move: GameMove):
    """
    Make a game move.
    Validates:
    - Game exists and is active
    - It's the player's turn
    - Action is valid for current game phase
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
        
    # Check if player exists in game
    if game_id not in game_players or move.player_id not in game_players[game_id]:
        raise HTTPException(status_code=404, detail="Player not found in game")
        
    # Get game manager
    game_manager = game_sessions[game_id]
    
    # Process the move
    if move.move_type == GameAction.ROLL_DICE:
        game_manager.roll_dice()
        game_manager.start_turn()

        return GameResponse(
            status="success",
            message="Dice rolled",
            data={}
        )
    # implement select
    elif move.move_type == GameAction.SELECT_PAIR:
        # Check if move data is valid
        if "pair_index" not in move.move_data:
            raise HTTPException(status_code=400, detail="Invalid move data. Missing pair_index")
        game_manager.select_pair(move.move_data["pair_index"])
        return GameResponse(
            status="success",
            message="Pair selected",
            data={}
        )
    # implement end review
    elif move.move_type == GameAction.END_REVIEW:
        game_manager.end_review()
        return GameResponse(
            status="success",
            message="Review ended",
            data={}
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid move type")

@router.get("/games/{game_id}/state", response_model=GameResponse)
async def get_game_state(game_id: str, player_id: str = Query(..., description="ID of the player requesting the state")):
    """
    Get current game state including:
    - Available card pairs
    - Current stock price
    - Selected pairs
    - Player hands
    - Current phase
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if player is part of the game
    if game_id not in game_players or player_id not in game_players[game_id]:
        raise HTTPException(status_code=403, detail="Player not part of this game")
    
    # Get game manager and player
    game_manager = game_sessions[game_id]
    player = game_players[game_id][player_id]

    # Create board data
    board_data = game_manager.context.create_board_for_player(player.player_id)
    
    return GameResponse(
        status="success",
        message="Game state retrieved successfully",
        data=board_data.dict()  # Convert Board model to dict
    )