import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting Local AI Agent Backend on http://{settings.HOST}:{settings.PORT}")
    print(f"📡 Target Ollama Instance: {settings.OLLAMA_BASE_URL}")
    print(f"📖 Swagger API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
