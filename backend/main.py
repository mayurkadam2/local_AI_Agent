import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.routes.health import router as health_router
from backend.routes.models import router as models_router
from backend.routes.chat import router as chat_router
from backend.routes.agent_routes import router as agent_router

app = FastAPI(
    title="Local AI Agent API",
    description="Backend API connecting to local Ollama instance for modular frontends and AI agents.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(health_router)
app.include_router(models_router)
app.include_router(chat_router)
app.include_router(agent_router)

@app.get("/api")
async def root():
    return {
        "message": "Local AI Agent API is running",
        "docs": "/docs",
        "endpoints": [
            "/api/health",
            "/api/models",
            "/api/chat",
            "/api/chat/stream",
            "/api/agent/status",
            "/api/agent/run"
        ]
    }

# Optionally mount frontend static files if directory exists
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
