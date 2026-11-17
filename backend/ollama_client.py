import httpx
from typing import AsyncGenerator, Dict, Any, List, Optional
from backend.config import settings

class OllamaClient:
    """Manager for connecting to and interacting with the local Ollama service."""

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, timeout: float = settings.REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def check_connection(self) -> Dict[str, Any]:
        """Verify if Ollama service is reachable and return status info."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/")
                if res.status_code == 200:
                    # Check version endpoint if available
                    version_info = "unknown"
                    try:
                        v_res = await client.get(f"{self.base_url}/api/version")
                        if v_res.status_code == 200:
                            version_info = v_res.json().get("version", "unknown")
                    except Exception:
                        pass

                    return {
                        "connected": True,
                        "status": "online",
                        "message": "Ollama service is reachable",
                        "base_url": self.base_url,
                        "version": version_info
                    }
                else:
                    return {
                        "connected": False,
                        "status": "error",
                        "message": f"Ollama returned HTTP status {res.status_code}",
                        "base_url": self.base_url
                    }
        except httpx.ConnectError:
            return {
                "connected": False,
                "status": "offline",
                "message": f"Could not connect to Ollama at {self.base_url}. Please ensure 'ollama serve' is running.",
                "base_url": self.base_url
            }
        except Exception as e:
            return {
                "connected": False,
                "status": "error",
                "message": f"Connection check failed: {str(e)}",
                "base_url": self.base_url
            }

    async def list_models(self) -> Dict[str, Any]:
        """Fetch list of available local models installed in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    for item in data.get("models", []):
                        models.append({
                            "name": item.get("name"),
                            "size_bytes": item.get("size"),
                            "size_human": f"{item.get('size', 0) / (1024**3):.2f} GB",
                            "modified_at": item.get("modified_at"),
                            "details": item.get("details", {})
                        })
                    return {
                        "success": True,
                        "models": models,
                        "count": len(models)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch models: HTTP {res.status_code}",
                        "models": []
                    }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Ollama is offline. Start Ollama server to view models.",
                "models": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching models: {str(e)}",
                "models": []
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a standard non-streaming chat completion request."""
        target_model = model or settings.DEFAULT_MODEL
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        if system_prompt:
            # Prepend system prompt if not already present
            if not any(m.get("role") == "system" for m in messages):
                payload["messages"] = [{"role": "system", "content": system_prompt}] + messages

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "success": True,
                        "model": target_model,
                        "message": data.get("message", {}),
                        "done": data.get("done", True),
                        "total_duration": data.get("total_duration"),
                        "eval_count": data.get("eval_count"),
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Ollama error: HTTP {res.status_code} - {res.text}"
                    }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Ollama is offline or unreachable at {self.base_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat request failed: {str(e)}"
            }

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat tokens from Ollama as ndjson."""
        target_model = model or settings.DEFAULT_MODEL
        formatted_messages = list(messages)
        if system_prompt and not any(m.get("role") == "system" for m in messages):
            formatted_messages = [{"role": "system", "content": system_prompt}] + formatted_messages

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": True,
        }
        if options:
            payload["options"] = options

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                if response.status_code != 200:
                    yield f'{{"error": "HTTP {response.status_code}"}}\n'
                    return
                async for chunk in response.aiter_text():
                    yield chunk

# Singleton client instance
ollama_client = OllamaClient()
