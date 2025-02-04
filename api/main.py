from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Add src to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.chat_agent import AnnieMacAgent
from src.models.database import init_db, Base, engine, Artist
import json
import asyncio

app = FastAPI()

# Create async session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store chat agents for different sessions
chat_agents = {}

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    artist_recommendations: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "Annie Mac Chat API is running"}

@app.get("/artists")
async def get_artists():
    try:
        async with async_session() as session:
            result = await session.execute("SELECT name FROM artists")
            artists = [row[0] for row in result]
            return {"artists": artists}
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

@app.websocket("/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    
    if client_id not in chat_agents:
        chat_agents[client_id] = AnnieMacAgent()
    
    try:
        while True:
            message = await websocket.receive_text()
            response = await chat_agents[client_id].chat(message)
            await websocket.send_text(json.dumps({
                "response": response,
                "type": "assistant"
            }))
    except Exception as e:
        print(f"Error in websocket: {str(e)}")
    finally:
        if client_id in chat_agents:
            del chat_agents[client_id]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_agents[request.user_id].chat(request.message)
        return ChatResponse(
            response=response,
            artist_recommendations=[]  # TODO: Extract recommendations from response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/artist/{artist_name}")
async def get_artist_info(artist_name: str):
    agent = AnnieMacAgent()
    artist_info = agent.get_artist_info(artist_name)
    if not artist_info:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist_info 