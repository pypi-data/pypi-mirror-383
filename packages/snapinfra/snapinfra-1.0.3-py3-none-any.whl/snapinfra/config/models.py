"""Configuration data models for AIAC."""

import os
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator


class BackendType(str, Enum):
    """Supported backend types."""
    
    OPENAI = "openai"
    GROQ = "groq"
    BEDROCK = "bedrock"
    OLLAMA = "ollama"


class BackendConfig(BaseModel):
    """Configuration for a single backend."""
    
    type: BackendType = Field(
        ...,
        description="Type of the backend (LLM provider)"
    )
    
    # OpenAI/Azure OpenAI specific
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication"
    )
    url: Optional[str] = Field(
        default=None,
        description="Custom URL for the backend API"
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version to use (e.g., for Azure OpenAI)"
    )
    
    # AWS Bedrock specific
    aws_profile: Optional[str] = Field(
        default=None,
        description="AWS profile name from credentials file"
    )
    aws_region: Optional[str] = Field(
        default=None,
        description="AWS region where models are hosted"
    )
    
    # Common configuration
    default_model: Optional[str] = Field(
        default=None,
        description="Default model to use when none is specified"
    )
    extra_headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Extra HTTP headers for requests"
    )
    
    @field_validator("api_key", "aws_profile", "aws_region", "url", "default_model")
    @classmethod
    def expand_env_vars(cls, v: Optional[str]) -> Optional[str]:
        """Expand environment variables in configuration values."""
        if v is None:
            return v
        return os.path.expandvars(v)


class Config(BaseModel):
    """Main AIAC configuration."""
    
    backends: Dict[str, BackendConfig] = Field(
        ...,
        description="Named backend configurations"
    )
    default_backend: Optional[str] = Field(
        default=None,
        description="Name of the default backend to use"
    )
    pure_ai_generation: bool = Field(
        default=True,
        description="Force pure AI-driven project generation (no fallback templates)"
    )
    validation_enabled: bool = Field(
        default=True,
        description="Enable comprehensive validation checks for generated code"
    )
    auto_fix_enabled: bool = Field(
        default=True,
        description="Enable automatic fixing of common code issues"
    )
    
    def get_backend_config(self, name: Optional[str] = None) -> tuple[str, BackendConfig]:
        """
        Get backend configuration by name or default.
        
        Args:
            name: Backend name, or None to use default
            
        Returns:
            Tuple of (backend_name, backend_config)
            
        Raises:
            ConfigurationError: If backend not found or no default set
        """
        from ..types.exceptions import ErrNoDefaultBackend, ErrNoSuchBackend
        
        if name is None:
            if self.default_backend is None:
                raise ErrNoDefaultBackend()
            name = self.default_backend
            
        if name not in self.backends:
            raise ErrNoSuchBackend(name)
            
        return name, self.backends[name]