from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connection: dict[str: WebSocket] = {}

    async def connect(self, id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[id] = websocket

    def disconnect(self, id: str):
        del self.active_connection[id]

    async def send_personal_message(self, id: str, message: str):
        websocket = self.active_connection[id]
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for id in self.active_connection:
            websocket = self.active_connection[id]
            await websocket.send_text(message)
