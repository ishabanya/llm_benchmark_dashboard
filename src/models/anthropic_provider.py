"""Anthropic provider implementation."""

import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import anthropic

from .base import LLMProvider, ModelResponse, ModelConfig


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # Set cost per token based on model
        self._set_pricing()
    
    def _set_pricing(self) -> None:
        """Set pricing based on model name."""
        pricing_map = {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-2.1": {"input": 0.008, "output": 0.024},
            "claude-2.0": {"input": 0.008, "output": 0.024},
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
        """Generate a response using Anthropic API."""
        start_time = time.time()
        
        try:
            kwargs = {
                "model": self.config.model_name,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = await self.client.messages.create(**kwargs)
            
            latency_ms = (time.time() - start_time) * 1000
            
            usage = response.usage
            prompt_tokens = usage.input_tokens
            completion_tokens = usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            content = ""
            if response.content and len(response.content) > 0:
                content = response.content[0].text
            
            return ModelResponse(
                content=content,
                model=self.config.model_name,
                provider=self.name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                timestamp=datetime.now(),
                metadata={
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    async def is_available(self) -> bool:
        """Check if Anthropic API is available."""
        try:
            # Simple test request
            await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information."""
        return {
            "provider": self.name,
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "cost_per_input_token": self.config.cost_per_input_token,
            "cost_per_output_token": self.config.cost_per_output_token,
        }