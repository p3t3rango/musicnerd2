from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.agent.chat_agent import AnnieMacAgent
import json
import asyncio

app = FastAPI()

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
    agent = AnnieMacAgent()
    with agent.engine.connect() as conn:
        result = conn.execute("SELECT name FROM artists")
        artists = [row[0] for row in result]
    return {"artists": artists}

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