"""Ollama provider implementation for local models."""

import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp
import asyncio

from .base import LLMProvider, ModelResponse, ModelConfig


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Local models have no token costs
        self.config.cost_per_input_token = 0.0
        self.config.cost_per_output_token = 0.0
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        """Generate a response using Ollama API."""
        start_time = time.time()
        
        # Construct the full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        
        payload = {
            "model": self.config.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
                "top_p": self.config.top_p,
            }
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Ollama API returned status {response.status}")
                    
                    result = await response.json()
                    
                    latency_ms = (time.time() - start_time) * 1000
                    
                    # Estimate token counts (Ollama doesn't provide exact counts)
                    prompt_tokens = self._estimate_tokens(full_prompt)
                    completion_tokens = self._estimate_tokens(result.get("response", ""))
                    total_tokens = prompt_tokens + completion_tokens
                    
                    return ModelResponse(
                        content=result.get("response", ""),
                        model=self.config.model_name,
                        provider=self.name,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        cost_usd=0.0,  # Local models are free
                        latency_ms=latency_ms,
                        timestamp=datetime.now(),
                        metadata={
                            "context": result.get("context", []),
                            "created_at": result.get("created_at", ""),
                            "done": result.get("done", False)
                        }
                    )
                    
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count (4 chars = 1 token)."""
        return max(1, len(text) // 4)
    
    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        models = await response.json()
                        model_names = [m["name"] for m in models.get("models", [])]
                        return self.config.model_name in model_names
                    return False
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information."""
        return {
            "provider": self.name,
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "cost_per_input_token": 0.0,
            "cost_per_output_token": 0.0,
            "base_url": self.base_url
        }