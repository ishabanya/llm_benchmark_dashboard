"""Test cases for model providers."""

import pytest
import os
from unittest.mock import Mock, patch
from datetime import datetime

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.base import ModelConfig, ModelResponse
from models.factory import ModelFactory
from models.openai_provider import OpenAIProvider
from models.anthropic_provider import AnthropicProvider
from models.ollama_provider import OllamaProvider


class TestModelConfig:
    """Test model configuration."""
    
    def test_model_config_creation(self):
        config = ModelConfig(
            model_name="gpt-4",
            provider="openai",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert config.model_name == "gpt-4"
        assert config.provider == "openai"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000


class TestModelFactory:
    """Test model factory."""
    
    def test_get_available_providers(self):
        providers = ModelFactory.get_available_providers()
        
        assert "openai" in providers
        assert "anthropic" in providers
        assert "ollama" in providers
    
    def test_create_openai_provider(self):
        config = ModelConfig(
            model_name="gpt-4",
            provider="openai"
        )
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = ModelFactory.create_provider(config)
            assert isinstance(provider, OpenAIProvider)
    
    def test_create_anthropic_provider(self):
        config = ModelConfig(
            model_name="claude-3-sonnet",
            provider="anthropic"
        )
        
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = ModelFactory.create_provider(config)
            assert isinstance(provider, AnthropicProvider)
    
    def test_create_ollama_provider(self):
        config = ModelConfig(
            model_name="llama2:7b",
            provider="ollama"
        )
        
        provider = ModelFactory.create_provider(config)
        assert isinstance(provider, OllamaProvider)
    
    def test_unknown_provider_raises_error(self):
        config = ModelConfig(
            model_name="unknown-model",
            provider="unknown"
        )
        
        with pytest.raises(ValueError, match="Unknown provider"):
            ModelFactory.create_provider(config)


class TestOpenAIProvider:
    """Test OpenAI provider."""
    
    def setup_method(self):
        self.config = ModelConfig(
            model_name="gpt-4",
            provider="openai",
            temperature=0.7,
            max_tokens=100
        )
    
    def test_pricing_setup(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider(self.config)
            
            # Should set pricing for GPT-4
            assert provider.config.cost_per_input_token > 0
            assert provider.config.cost_per_output_token > 0
    
    def test_cost_calculation(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider(self.config)
            
            cost = provider.calculate_cost(1000, 500)
            assert cost > 0
            assert isinstance(cost, float)
    
    def test_get_model_info(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider(self.config)
            info = provider.get_model_info()
            
            assert info["provider"] == "openai"
            assert info["model"] == "gpt-4"
            assert "cost_per_input_token" in info


class TestAnthropicProvider:
    """Test Anthropic provider."""
    
    def setup_method(self):
        self.config = ModelConfig(
            model_name="claude-3-sonnet",
            provider="anthropic",
            temperature=0.7,
            max_tokens=100
        )
    
    def test_pricing_setup(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider(self.config)
            
            # Should set pricing for Claude
            assert provider.config.cost_per_input_token > 0
            assert provider.config.cost_per_output_token > 0
    
    def test_get_model_info(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider(self.config)
            info = provider.get_model_info()
            
            assert info["provider"] == "anthropic"
            assert info["model"] == "claude-3-sonnet"


class TestOllamaProvider:
    """Test Ollama provider."""
    
    def setup_method(self):
        self.config = ModelConfig(
            model_name="llama2:7b",
            provider="ollama"
        )
    
    def test_zero_cost_pricing(self):
        provider = OllamaProvider(self.config)
        
        # Local models should have zero cost
        assert provider.config.cost_per_input_token == 0.0
        assert provider.config.cost_per_output_token == 0.0
    
    def test_token_estimation(self):
        provider = OllamaProvider(self.config)
        
        text = "This is a test sentence."
        tokens = provider._estimate_tokens(text)
        
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_get_model_info(self):
        provider = OllamaProvider(self.config)
        info = provider.get_model_info()
        
        assert info["provider"] == "ollama"
        assert info["model"] == "llama2:7b"
        assert info["cost_per_input_token"] == 0.0
        assert "base_url" in info


class TestModelResponse:
    """Test model response structure."""
    
    def test_model_response_creation(self):
        response = ModelResponse(
            content="Test response",
            model="test-model",
            provider="test",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            cost_usd=0.001,
            latency_ms=100.0,
            timestamp=datetime.now(),
            metadata={"test": "data"}
        )
        
        assert response.content == "Test response"
        assert response.model == "test-model"
        assert response.provider == "test"
        assert response.total_tokens == 30
        assert response.cost_usd == 0.001
        assert "test" in response.metadata