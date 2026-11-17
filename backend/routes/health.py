from fastapi import APIRouter
from backend.ollama_client import ollama_client

router = APIRouter(prefix="/api/health", tags=["Health & Connection"])

@router.get("")
async def get_health():
    """
    Check backend API health and verify Ollama connection.
    """
    ollama_status = await ollama_client.check_connection()
    return {
        "status": "healthy" if ollama_status.get("connected") else "degraded",
        "backend": "online",
        "ollama": ollama_status
    }
