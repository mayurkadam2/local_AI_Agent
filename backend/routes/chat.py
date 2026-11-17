from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.ollama_client import ollama_client

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = Field(None, description="Model identifier (e.g. 'qwen3.5:4b')")
    system_prompt: Optional[str] = Field(None, description="Optional system instruction")
    options: Optional[Dict[str, Any]] = Field(None, description="Optional Ollama inference parameters (temperature, etc.)")

@router.post("")
async def chat_completion(request: ChatRequest):
    """
    Standard synchronous chat completion with Ollama.
    """
    formatted_messages = [{"role": m.role, "content": m.content} for m in request.messages]
    response = await ollama_client.chat(
        messages=formatted_messages,
        model=request.model,
        system_prompt=request.system_prompt,
        options=request.options
    )
    if not response.get("success", False):
        raise HTTPException(status_code=502, detail=response.get("error", "Failed to communicate with Ollama"))
    return response

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream token-by-token response from Ollama.
    """
    formatted_messages = [{"role": m.role, "content": m.content} for m in request.messages]
    generator = ollama_client.chat_stream(
        messages=formatted_messages,
        model=request.model,
        system_prompt=request.system_prompt,
        options=request.options
    )
    return StreamingResponse(generator, media_type="application/x-ndjson")
