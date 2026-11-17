"""
Sample Agent Implementation
This is a lightweight modular agent template for local Ollama models.
Demonstrates the structure for reasoning, tool registration, and execution.
"""
from typing import Dict, Any, Callable
from datetime import datetime
from backend.ollama_client import ollama_client
from backend.config import settings

class SampleAgent:
    """A sample modular AI agent with tool-calling capabilities."""

    def __init__(self, name: str = "LocalAssistantAgent", model: str = settings.DEFAULT_MODEL):
        self.name = name
        self.model = model
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, description: str, func: Callable):
        """Register a new tool available to the agent."""
        self.tools[name] = {
            "description": description,
            "func": func
        }

    def _register_default_tools(self):
        """Register basic sample tools."""
        self.register_tool(
            "get_current_time",
            "Returns current system date and time",
            lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.register_tool(
            "calculator",
            "Performs basic arithmetic evaluation. Input format: expression string (e.g., '25 * 4')",
            self._safe_eval
        )

    def _safe_eval(self, expr: str) -> str:
        """Simple safe arithmetic evaluator."""
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in str(expr)):
            return "Error: Invalid characters in arithmetic expression."
        try:
            return str(eval(str(expr), {"__builtins__": {}}, {}))
        except Exception as e:
            return f"Eval error: {str(e)}"

    def get_system_prompt(self) -> str:
        tools_desc = "\n".join([f"- {name}: {t['description']}" for name, t in self.tools.items()])
        return (
            f"You are {self.name}, a helpful AI agent running locally via Ollama.\n"
            f"You have access to the following sample tools:\n{tools_desc}\n"
            "Respond helpfully, clearly, and concisely to the user."
        )

    async def run(self, user_prompt: str) -> Dict[str, Any]:
        """
        Sample agent execution pipeline:
        1. Prepares messages with system prompt and registered tools description
        2. Queries Ollama local model
        3. Returns structured output
        """
        system_prompt = self.get_system_prompt()
        messages = [
            {"role": "user", "content": user_prompt}
        ]

        response = await ollama_client.chat(
            messages=messages,
            model=self.model,
            system_prompt=system_prompt
        )

        return {
            "agent": self.name,
            "model_used": self.model,
            "tools_available": list(self.tools.keys()),
            "status": "success" if response.get("success") else "error",
            "prompt": user_prompt,
            "response": response.get("message", {}).get("content", ""),
            "raw_ollama_response": response
        }

# Singleton sample instance
sample_agent = SampleAgent()
