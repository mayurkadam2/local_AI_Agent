from fastapi import APIRouter
from backend.ollama_client import ollama_client
from backend.config import settings

router = APIRouter(prefix="/api/models", tags=["Models"])

@router.get("")
async def get_models():
    """
    List all local models downloaded into Ollama.
    """
    result = await ollama_client.list_models()
    result["default_model"] = settings.DEFAULT_MODEL
    return result
