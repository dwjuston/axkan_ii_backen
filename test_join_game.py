import asyncio
import websockets
import json
import requests

async def test_join_game():
    # Join existing game
    game_id = "3ce5af76-a1eb-46cc-ae6a-09518a3a3ddc"  # Use the game ID from the first client
    response = requests.post(f'http://localhost:8000/api/v1/games/{game_id}/join', 
                           json={"player_name": "Player2"})
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code != 200:
        print("Failed to join game")
        return
        
    # Connect to WebSocket
    uri = f"ws://localhost:8000/api/v1/games/{game_id}/ws"
    print(f"Connecting to WebSocket at: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Wait for notifications
            while True:
                try:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed by server")
                    break
                    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_join_game()) 