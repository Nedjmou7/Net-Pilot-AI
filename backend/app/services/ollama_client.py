import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
from app.config import settings

logger = logging.getLogger("topogemma.ollama")

class OllamaClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama service is reachable and list available models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_loaded = any(self.model in m for m in models)
                    return {
                        "status": "online",
                        "ollama_connected": True,
                        "model": self.model,
                        "model_available": model_loaded,
                        "models_installed": models
                    }
                return {
                    "status": "degraded",
                    "ollama_connected": True,
                    "model": self.model,
                    "model_available": False,
                    "error": f"HTTP {res.status_code}"
                }
        except Exception as e:
            return {
                "status": "offline",
                "ollama_connected": False,
                "model": self.model,
                "model_available": False,
                "error": str(e)
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        format_json: bool = False,
        temperature: float = 0.2,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call Ollama /api/chat with non-streaming request."""
        target_model = model or self.model
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if format_json:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        format_json: bool = False,
        temperature: float = 0.2,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from Ollama /api/chat."""
        target_model = model or self.model
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        if format_json:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

ollama_client = OllamaClient()
