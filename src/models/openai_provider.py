"""OpenAI provider implementation."""

import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import openai
from openai import AsyncOpenAI

from .base import LLMProvider, ModelResponse, ModelConfig


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Set cost per token based on model
        self._set_pricing()
    
    def _set_pricing(self) -> None:
        """Set pricing based on model name."""
        pricing_map = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
        }
        
        model_key = self.config.model_name.lower()
        for key, pricing in pricing_map.items():
            if key in model_key:
                self.config.cost_per_input_token = pricing["input"]
                self.config.cost_per_output_token = pricing["output"]
                break
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        """Generate a response using OpenAI API."""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                timeout=self.config.timeout
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            return ModelResponse(
                content=response.choices[0].message.content or "",
                model=self.config.model_name,
                provider=self.name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                timestamp=datetime.now(),
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "system_fingerprint": getattr(response, "system_fingerprint", None)
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": self.name,
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "cost_per_input_token": self.config.cost_per_input_token,
            "cost_per_output_token": self.config.cost_per_output_token,
        }