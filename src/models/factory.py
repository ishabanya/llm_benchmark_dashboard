"""Factory for creating LLM providers."""

from typing import Dict, Type

from .base import LLMProvider, ModelConfig
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider


class ModelFactory:
    """Factory for creating LLM providers."""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }
    
    @classmethod
    def create_provider(cls, config: ModelConfig) -> LLMProvider:
        """Create a provider instance based on configuration."""
        provider_class = cls._providers.get(config.provider.lower())
        if not provider_class:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider '{config.provider}'. "
                f"Available providers: {available}"
            )
        
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(
        cls, 
        name: str, 
        provider_class: Type[LLMProvider]
    ) -> None:
        """Register a new provider."""
        cls._providers[name.lower()] = provider_class