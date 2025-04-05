import asyncio

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List, Optional
import uuid
import json

from board import Board
from enums import GameAction, GamePhase
from game_context import GameResult
from game_manager import GameManager
from .models import JoinGameRequest, GameMove, GameMetadata, GameResponse, GameError, PlayerMetadata
from .websocket import websocket_manager
from player import Player, PlayerView


router = APIRouter()

# In-memory storage for game sessions
game_sessions: Dict[str, GameManager] = {}
# Track which players have joined each game
game_players: Dict[str, Dict[str, Player]] = {}

# clear all in-memory game session
@router.post("/games/clear")
async def clear_game_sessions() -> None:
    """
    Clear all game sessions and player data.
    """
    global game_sessions, game_players
    game_sessions = {}
    game_players = {}


@router.post("/games/join", response_model=PlayerMetadata)
async def join_game(request: JoinGameRequest):
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
        player_uuid = str(uuid.uuid4())
        
        # Create second player
        player2 = Player(player_id=1, uuid=player_uuid, name=request.player_name)
        game_players[game_id][player_uuid] = player2
        game_manager = game_sessions[game_id]

        # Start the game
        await game_manager.take_action(player_uuid=player_uuid, action=GameAction.JOIN_GAME, player_name=request.player_name)

        return PlayerMetadata(
            game_id=game_id,
            player_uuid=player_uuid,
            player_name=request.player_name,
            opponent_uuid=list(game_players[game_id].values())[0].uuid,
            opponent_name=list(game_players[game_id].values())[0].name)

    else:
        # Create new game
        game_id = str(uuid.uuid4())
        player_uuid = str(uuid.uuid4())
        
        # Create first player
        player1 = Player(player_id=0, uuid=player_uuid, name=request.player_name)
        
        # Initialize game manager
        game_manager = GameManager(game_id=game_id)
        game_sessions[game_id] = game_manager
        game_players[game_id] = {player_uuid: player1}

        await game_manager.take_action(player_uuid=player_uuid, action=GameAction.JOIN_GAME, player_name=request.player_name)
        return PlayerMetadata(game_id=game_id, player_uuid=player_uuid, player_name=request.player_name, opponent_uuid=None, opponent_name=None)

# game ready
@router.post("/games/ready", response_model=GameResponse)
async def ready_game(game_id: str, player_uuid: str = Query(..., description="ID of the player getting ready")):
    """
    Mark a player as ready to start the game.
    If both players are ready, the game starts.
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if player is part of the game
    if game_id not in game_players or player_uuid not in game_players[game_id]:
        raise HTTPException(status_code=403, detail="Player not part of this game")

    # Get game manager
    game_manager = game_sessions[game_id]

    # Process the ready action
    await game_manager.take_action(player_uuid, GameAction.READY)
    return GameResponse(
        status="success",
        game_id=game_id,
        player_uuid=player_uuid
    )

# Roll dice, select pair, convert color, end review
@router.post("/games/roll-dice", response_model=GameResponse)
async def roll_dice(game_id: str, player_uuid: str, dice_collection_type: str = None, special_card_index: Optional[int] = None):
    """
    Roll the dice for the current player.
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if player is part of the game
    if game_id not in game_players or player_uuid not in game_players[game_id]:
        raise HTTPException(status_code=403, detail="Player not part of this game")

    # Get game manager
    game_manager = game_sessions[game_id]

    # Process the roll dice action
    await game_manager.take_action(player_uuid, GameAction.ROLL_DICE, dice_collection_type=dice_collection_type, special_card_index=special_card_index)

    return GameResponse(
        status="success",
        game_id=game_id,
        player_uuid=player_uuid
    )

@router.post("/games/select-pair", response_model=GameResponse)
async def select_pair(game_id: str, player_uuid: str, pair_index: int):
    """
    Select a pair for the current player.
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if player is part of the game
    if game_id not in game_players or player_uuid not in game_players[game_id]:
        raise HTTPException(status_code=403, detail="Player not part of this game")

    # Get game manager
    game_manager = game_sessions[game_id]

    # Process the select pair action
    await game_manager.take_action(player_uuid, GameAction.SELECT_PAIR, pair_index=pair_index)

    return GameResponse(
        status="success",
        game_id=game_id,
        player_uuid=player_uuid
    )

@router.post("/games/end-review", response_model=GameResponse)
async def end_review(game_id: str, player_uuid: str):
    """
    End the review phase.
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if player is part of the game
    if game_id not in game_players or player_uuid not in game_players[game_id]:
        raise HTTPException(status_code=403, detail="Player not part of this game")

    # Get game manager
    game_manager = game_sessions[game_id]

    # Process the end review action
    await game_manager.take_action(player_uuid, GameAction.END_REVIEW)

    return GameResponse(
        status="success",
        game_id=game_id,
        player_uuid=player_uuid
    )

# color convert
@router.post("/games/convert-color", response_model=GameResponse)
async def convert_color(game_id: str, player_uuid: str, pair_index: int, special_card_index: int):
    """
    Convert the color of a pair for the current player.
    """
    # Check if game exists
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if player is part of the game
    if game_id not in game_players or player_uuid not in game_players[game_id]:
        raise HTTPException(status_code=403, detail="Player not part of this game")

    # Get game manager
    game_manager = game_sessions[game_id]

    # Process the color convert action
    await game_manager.take_action(player_uuid, GameAction.COLOR_CONVERT, pair_index=pair_index, special_card_index=special_card_index)

    return GameResponse(
        status="success",
        game_id=game_id,
        player_uuid=player_uuid
    )

@router.websocket("/games/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    game_id: str,
    player_uuid: str = Query(..., description="ID of the player connecting")
):
    async def message_task():
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await websocket_manager.disconnect(websocket, game_id, player_uuid)
        except Exception as e:
            print(f"Error in WebSocket connection: {str(e)}")
            await websocket_manager.disconnect(websocket, game_id, player_uuid)

    # Check if game exists
    if game_id not in game_sessions:
        await websocket.close(code=4004, reason="Game not found")
        return

    # Check if player is part of the game
    if game_id not in game_players or player_uuid not in game_players[game_id]:
        await websocket.close(code=4003, reason="Player not part of this game")
        return
    # Register the connection with the WebSocket manager
    await websocket_manager.connect(websocket, game_id, player_uuid)
    await asyncio.gather(message_task())



# an endpoint to ask server to ping the client
@router.post("/games/ping")
async def ping(game_id: str):
    # notify all clients a message ping
    await websocket_manager.send(game_id, None, "debug", "ping")


# endpoints to get sample data: Board, PlayerView, OpponentView, GameResult
#
@router.get("/games/sample/board", response_model=Board)
def get_sample_board():
    """
    Get a sample board data for testing.
    """
    board = Board.create_sample()
    return board

@router.get("/games/sample/game-result", response_model=GameResult)
def get_sample_game_result():
    """
    Get a sample board data for testing.
    """
    game_result = GameResult.create_sample()
    return game_result