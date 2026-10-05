from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_text(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

    async def broadcast_bytes(self, sender: WebSocket, bytes_data: bytes):
        for connection in self.active_connections:
            # إرسال البث للجميع بما في ذلك المرسل أو استثناؤه
            try:
                await connection.send_bytes(bytes_data)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    await manager.broadcast_text(f"System: User {username} joined")
    try:
        while True:
            # استقبال أي نوع من البيانات (نص أو باينري)
            message = await websocket.receive()
            if "text" in message and message["text"]:
                await manager.broadcast_text(f"{username}: {message['text']}")
            elif "bytes" in message and message["bytes"]:
                await manager.broadcast_bytes(websocket, message["bytes"])
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_text(f"System: User {username} left")