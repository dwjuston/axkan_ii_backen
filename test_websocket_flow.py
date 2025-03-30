import asyncio
import websockets
import json
import requests
import time

async def test_websocket_flow():
    print("\n=== Starting WebSocket Flow Test ===")
    
    # First client creates game
    response = requests.post('http://localhost:8000/api/v1/games', json={"player_name": "Player1"})
    print(f"\nPlayer1 create game response: {response.text}")
    game_data = response.json()
    game_id = game_data['data']['game_id']
    player1_id = game_data['data']['player_id']
    
    # Connect first client to WebSocket
    uri = f"ws://localhost:8000/api/v1/games/{game_id}/ws"
    
    async def client1():
        try:
            async with websockets.connect(uri) as websocket:
                print(f"\nPlayer1 connected to WebSocket with ID: {id(websocket)}")
                
                # Send a ping to verify connection
                await websocket.send(json.dumps({"type": "ping"}))
                print("\nPlayer1 sent ping")
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"\n=== Player1 Received Message ===")
                        print(f"Raw message: {message}")
                        print(f"Message type: {data.get('type')}")
                        print(f"Message data: {data.get('data')}")
                        print(f"Timestamp: {time.strftime('%H:%M:%S')}")
                        print("================================")
                    except websockets.ConnectionClosed:
                        print("\nPlayer1 connection closed normally")
                        break
                    except Exception as e:
                        print(f"\nPlayer1 error: {str(e)}")
                        break
        except Exception as e:
            print(f"\nPlayer1 connection error: {str(e)}")
    
    # Start client1's WebSocket connection
    client1_task = asyncio.create_task(client1())
    
    # Wait a bit for client1 to connect
    await asyncio.sleep(1)
    
    # Second client joins game
    response = requests.post('http://localhost:8000/api/v1/games', json={"player_name": "Player2"})
    print(f"\nPlayer2 join game response: {response.text}")
    player2_data = response.json()
    player2_id = player2_data['data']['player_id']
    
    async def client2():
        try:
            async with websockets.connect(uri) as websocket:
                print(f"\nPlayer2 connected to WebSocket with ID: {id(websocket)}")
                
                # Send a ping to verify connection
                await websocket.send(json.dumps({"type": "ping"}))
                print("\nPlayer2 sent ping")
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"\n=== Player2 Received Message ===")
                        print(f"Raw message: {message}")
                        print(f"Message type: {data.get('type')}")
                        print(f"Message data: {data.get('data')}")
                        print(f"Timestamp: {time.strftime('%H:%M:%S')}")
                        print("================================")
                    except websockets.ConnectionClosed:
                        print("\nPlayer2 connection closed normally")
                        break
                    except Exception as e:
                        print(f"\nPlayer2 error: {str(e)}")
                        break
        except Exception as e:
            print(f"\nPlayer2 connection error: {str(e)}")
    
    # Start client2's WebSocket connection
    client2_task = asyncio.create_task(client2())
    
    # Keep connections alive for a few seconds to receive notifications
    print("\nWaiting for notifications...")
    await asyncio.sleep(5)
    
    # Cancel the tasks gracefully
    client1_task.cancel()
    client2_task.cancel()
    try:
        await client1_task
        await client2_task
    except asyncio.CancelledError:
        print("\nWebSocket connections closed")

if __name__ == "__main__":
    asyncio.run(test_websocket_flow()) 