import asyncio
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        if not self.active_connections:
            return
        tasks = [self._safe_send_json(conn, message)
                 for conn in self.active_connections]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send_json(self, websocket: WebSocket, message: dict) -> None:
        try:
            await websocket.send_json(message)
        except Exception:
            pass


# 🔥 MAKE SURE THIS EXACT LINE IS PRESENT AT THE BOTTOM OF THE FILE:
socket_manager = ConnectionManager()
