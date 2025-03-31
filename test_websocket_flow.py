import asyncio
import websockets
import json
import requests
import time
import pytest
import logging
import sys

# Configure logging to output to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create a logger for the test
logger = logging.getLogger('test_websocket')
logger.setLevel(logging.INFO)

# Create a logger for the server
server_logger = logging.getLogger('server')
server_logger.setLevel(logging.INFO)

@pytest.mark.asyncio
async def test_websocket_flow():
    logger.info("\n=== Starting WebSocket Flow Test ===")
    
    # First client creates game
    response = requests.post('http://localhost:8000/api/v1/games', json={"player_name": "Player1"})
    logger.info(f"\nPlayer1 create game response: {response.text}")
    game_data = response.json()
    game_id = game_data['data']['game_id']
    player1_id = game_data['data']['player_id']
    
    # Connect first client to WebSocket with player_id
    uri = f"ws://localhost:8000/api/v1/games/{game_id}/ws?player_id={player1_id}"
    
    async def client1():
        try:
            async with websockets.connect(uri) as websocket:
                connection_id = id(websocket)
                logger.info(f"\nPlayer1 connected to WebSocket with ID: {connection_id}")
                logger.info(f"Connection object: {websocket}")
                
                # Send a ping to verify connection
                await websocket.send(json.dumps({"type": "ping"}))
                logger.info("\nPlayer1 sent ping")
                
                while True:
                    try:
                        message = await websocket.recv()
                        logger.info(f"\n=== Player1 Received Message ===")
                        logger.info(f"Raw message: {message}")
                        # Parse the message
                        data = json.loads(json.loads(message) if isinstance(message, str) else message)
                        logger.info(f"Message type: {data['type']}")
                        logger.info(f"Message data: {data['data']}")
                        logger.info(f"Timestamp: {data['timestamp']}")
                        logger.info(f"Game ID: {data['game_id']}")
                        logger.info(f"Target players: {data['target_players']}")
                        logger.info("================================")
                    except websockets.ConnectionClosed:
                        logger.info("\nPlayer1 connection closed normally")
                        break
                    except Exception as e:
                        logger.error(f"\nPlayer1 error: {str(e)}")
                        break
        except Exception as e:
            logger.error(f"\nPlayer1 connection error: {str(e)}")
    
    # Start client1's WebSocket connection
    client1_task = asyncio.create_task(client1())
    
    # Wait a bit for client1 to connect
    await asyncio.sleep(1)
    
    async def client2():
        try:
            # First join the game to get player2_id
            response = requests.post('http://localhost:8000/api/v1/games', json={"player_name": "Player2"})
            logger.info(f"\nPlayer2 join game response: {response.text}")
            player2_data = response.json()
            player2_id = player2_data['data']['player_id']
            
            # Now connect to WebSocket with player2_id
            uri2 = f"ws://localhost:8000/api/v1/games/{game_id}/ws?player_id={player2_id}"
            async with websockets.connect(uri2) as websocket2:
                connection_id = id(websocket2)
                logger.info(f"\nPlayer2 connected to WebSocket with ID: {connection_id}")
                logger.info(f"Connection object: {websocket2}")
                
                # Send a ping to verify connection
                await websocket2.send(json.dumps({"type": "ping"}))
                logger.info("\nPlayer2 sent ping")
                
                while True:
                    try:
                        message = await websocket2.recv()
                        logger.info(f"\n=== Player2 Received Message ===")
                        logger.info(f"Raw message: {message}")
                        # Parse the message
                        data = json.loads(json.loads(message) if isinstance(message, str) else message)
                        logger.info(f"Message type: {data['type']}")
                        logger.info(f"Message data: {data['data']}")
                        logger.info(f"Timestamp: {data['timestamp']}")
                        logger.info(f"Game ID: {data['game_id']}")
                        logger.info(f"Target players: {data['target_players']}")
                        logger.info("================================")
                    except websockets.ConnectionClosed:
                        logger.info("\nPlayer2 connection closed normally")
                        break
                    except Exception as e:
                        logger.error(f"\nPlayer2 error: {str(e)}")
                        break
        except Exception as e:
            logger.error(f"\nPlayer2 connection error: {str(e)}")
    
    # Start client2's WebSocket connection and game join
    client2_task = asyncio.create_task(client2())
    
    # Keep connections alive for a few seconds to receive notifications
    logger.info("\nWaiting for notifications...")
    await asyncio.sleep(5)
    
    # Cancel the tasks gracefully
    client1_task.cancel()
    client2_task.cancel()
    try:
        await client1_task
        await client2_task
    except asyncio.CancelledError:
        logger.info("\nWebSocket connections closed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--log-cli-level=INFO"]) 