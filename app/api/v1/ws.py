from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket import socket_manager

router = APIRouter(prefix="/ws", tags=["Real-time Live Engine"])

@router.websocket("/admin/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    Exposes a persistent, bidirectional WebSocket pipeline for the Admin Dashboard.
    Registers listeners into the broadcast pool and handles clean dropouts.
    """
    # 1. Accept the persistent handshake and register the socket channel
    await socket_manager.connect(websocket)
    
    try:
        # 2. Keep the context socket channel open indefinitely
        while True:
            # We look for any incoming heartbeats or pings from the client
            # This keeps the TCP loop alive and active
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        # 3. If the dashboard disconnects or crashes, clean up memory instantly
        socket_manager.disconnect(websocket)
