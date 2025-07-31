
# backend/connection_manager.py
# --- Final Version ---

from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)

    async def broadcast_to_users(self, message: dict, user_ids: List[int]):
        for user_id in user_ids:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await websocket.send_json(message)

manager = ConnectionManager()