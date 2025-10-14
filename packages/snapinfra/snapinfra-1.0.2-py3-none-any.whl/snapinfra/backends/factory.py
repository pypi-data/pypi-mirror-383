"""Backend factory for creating backend instances."""

from ..config.models import BackendConfig, BackendType
from ..types import Backend
from .bedrock import BedrockBackend
from .groq import GroqBackend
from .ollama import OllamaBackend
from .openai import OpenAIBackend


def create_backend(config: BackendConfig) -> Backend:
    """
    Create a backend instance from configuration.
    
    Args:
        config: Backend configuration
        
    Returns:
        Backend instance
        
    Raises:
        ValueError: If backend type is unsupported
    """
    if config.type == BackendType.OPENAI:
        return OpenAIBackend(
            api_key=config.api_key,
            base_url=config.url,
            api_version=config.api_version,
            extra_headers=config.extra_headers
        )
    elif config.type == BackendType.GROQ:
        return GroqBackend(
            api_key=config.api_key,
            base_url=config.url,
            extra_headers=config.extra_headers
        )
    elif config.type == BackendType.BEDROCK:
        return BedrockBackend(
            aws_profile=config.aws_profile,
            aws_region=config.aws_region or "us-east-1"
        )
    elif config.type == BackendType.OLLAMA:
        return OllamaBackend(
            base_url=config.url or "http://localhost:11434/api",
            extra_headers=config.extra_headers
        )
    else:
        raise ValueError(f"Unsupported backend type: {config.type}")