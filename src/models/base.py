"""Base classes for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ModelResponse:
    """Response from an LLM model."""
    content: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    model_name: str
    provider: str
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    retry_attempts: int = 3
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.name = config.provider
        
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the model is available."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of a request."""
        input_cost = prompt_tokens * self.config.cost_per_input_token / 1000
        output_cost = completion_tokens * self.config.cost_per_output_token / 1000
        return input_cost + output_cost