import os
from pydantic import BaseModel

class Settings(BaseModel):
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen3.5:4b")
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "60.0"))
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "*",  # Allow all during local development
    ]

settings = Settings()
