# test_ws_client.py
import asyncio
import websockets  # Run 'uv add websockets' if missing


async def listen():
    url = "ws://127.0.0.1:8000/api/v1/ws/admin/live"
    async with websockets.connect(url) as websocket:
        print("✅ Successfully connected to Admin Telemetry WebSocket Highway!")
        while True:
            msg = await websocket.recv()
            print(f"🚨 ALERT BROADCAST RECEIVED: {msg}")

if __name__ == "__main__":
    asyncio.run(listen())
