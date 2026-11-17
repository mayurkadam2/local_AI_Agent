from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from backend.agent.sample_agent import sample_agent

router = APIRouter(prefix="/api/agent", tags=["Agent"])

class AgentRunRequest(BaseModel):
    prompt: str = Field(..., description="Prompt or goal for the sample agent")
    model: Optional[str] = Field(None, description="Optional override model")

@router.get("/status")
async def get_agent_status():
    """Check agent configuration and available tools."""
    return {
        "agent_name": sample_agent.name,
        "model": sample_agent.model,
        "tools": {name: t["description"] for name, t in sample_agent.tools.items()},
        "status": "ready"
    }

@router.post("/run")
async def run_agent(request: AgentRunRequest):
    """Run a prompt through the sample agent pipeline."""
    if request.model:
        sample_agent.model = request.model
    result = await sample_agent.run(request.prompt)
    return result
