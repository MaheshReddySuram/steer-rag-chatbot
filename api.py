from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

from steer import SteerChatbot


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=5)


app = FastAPI(title="Steer RAG Chatbot API", version="1.0.0")
bot = SteerChatbot(policy_dir=ROOT / "data" / "policies")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    return bot.answer(request.question, top_k=request.top_k)
