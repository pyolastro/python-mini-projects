
import os, time
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from brains import Brain, RulesBrain, GroqBrain

# Config
API_KEY = os.getenv("BOT_API_KEY")  # set this to enable simple header auth
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*").split(",") 

# App & CORS
app = FastAPI(title="Web Chat Bot API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple memory
conversations: Dict[str, List[Dict]] = {}

# Auth
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

# Schemas
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    user_id: str
    context_len: int

# Bot logic
# choose a brain via env var
def make_brain() -> Brain:
    kind = os.getenv("BRAIN", "rules").lower()
    if kind == "groq":
        return GroqBrain()
    return RulesBrain()

BRAIN: Brain = make_brain()

def generate_reply(user_id: str, message: str) -> str:
    if message.strip().lower() == "reset":
        conversations[user_id] = []
        return "Conversation reset. What's next?"
    history = conversations.get(user_id, [])
    return BRAIN.reply(history, message)


# REST: POST /chat
@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, _=Depends(require_api_key)):
    user_id = body.user_id
    message = body.message

    conversations.setdefault(user_id, []).append({"role": "user", "text": message, "ts": time.time()})
    reply = generate_reply(user_id, message)
    conversations[user_id].append({"role": "bot", "text": reply, "ts": time.time()})
    return ChatResponse(reply=reply, user_id=user_id, context_len=len(conversations[user_id]))

# REST: GET last N messages
@app.get("/history/{user_id}")
def history(user_id: str, n: int = 20, _=Depends(require_api_key)):
    return conversations.get(user_id, [])[-n:]

# WebSocket: /ws/{user_id}
@app.websocket("/ws/{user_id}")
async def ws_endpoint(ws: WebSocket, user_id: str):
    key = ws.query_params.get("key")
    if API_KEY and key != API_KEY:
        await ws.close(code=4401); return

    await ws.accept()
    conversations.setdefault(user_id, [])
    try:
        while True:
            user_text = await ws.receive_text()
            if user_text.strip().lower() == "reset":
                conversations[user_id] = []
                await ws.send_text("Conversation reset. What’s next?")
                continue

            # record user msg
            conversations[user_id].append({"role": "user", "text": user_text, "ts": time.time()})

            # stream tokens if the brain supports it
            try:
                chunk_buf = []
                full_text = ""

                async def flush():
                    nonlocal chunk_buf
                    if chunk_buf:
                        await ws.send_text("".join(chunk_buf))
                        chunk_buf = []

                for token in BRAIN.stream_reply(conversations[user_id], user_text):
                    full_text += token
                    chunk_buf.append(token)
                    # send 64+ chars at a time to avoid too many frames
                    if sum(len(t) for t in chunk_buf) >= 64:
                        await flush()
                await flush()
                bot_text = full_text
            except AttributeError:
                # non-streaming
                bot_text = BRAIN.reply(conversations[user_id], user_text)
                await ws.send_text(bot_text)

            # record bot msg
            conversations[user_id].append({"role": "bot", "text": bot_text, "ts": time.time()})
    except WebSocketDisconnect:
        return

# Serve frontend
app.mount("/", StaticFiles(directory="public", html=True), name="static")
