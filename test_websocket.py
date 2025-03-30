import asyncio
import websockets
import json
import requests

async def test_websocket():
    # First create a game
    response = requests.post('http://localhost:8000/api/v1/games', json={"player_name": "TestPlayer"})
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    game_data = response.json()
    print(f"Game data: {game_data}")
    
    if game_data.get('status') != 'success':
        print("Failed to create game")
        return
        
    game_id = game_data['data']['game_id']
    print(f"Created game with ID: {game_id}")
    
    # Connect to WebSocket
    uri = f"ws://localhost:8000/api/v1/games/{game_id}/ws"
    print(f"Connecting to WebSocket at: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Send a test message
            test_message = {"type": "test", "message": "Hello WebSocket!"}
            await websocket.send(json.dumps(test_message))
            print("Sent test message")
            
            # Wait for any response
            try:
                response = await websocket.recv()
                print(f"Received response: {response}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed by server")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 