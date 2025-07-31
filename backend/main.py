# backend/main.py
# --- Final Version ---

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

import models
from routers import auth, dashboards, tasks, comments
from connection_manager import manager
from dependencies import get_db
import crud

app = FastAPI(
    title="Task Dashboard API",
    description="API for a collaborative task management dashboard.",
    version="1.0.0",
)

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
if not os.path.exists('uploads'):
    os.makedirs('uploads')
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include all API routers
app.include_router(auth.router)
app.include_router(dashboards.router)
app.include_router(tasks.router)
app.include_router(comments.router)

# WebSocket Endpoint for real-time communication
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive, can be extended to receive messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the Task Dashboard API! Version 1.0"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app",
#                  port=8000, host= "localhost",reload=True
#                 )
