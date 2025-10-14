"""Tests for configuration loading and validation."""

import os
import tempfile
from pathlib import Path

import pytest

from snapinfra.config import load_config
from snapinfra.config.models import BackendType, Config
from snapinfra.types.exceptions import ConfigurationError


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_valid_config_loading(self):
        """Test loading a valid configuration file."""
        config_content = """
        default_backend = "openai"
        
        [backends.openai]
        type = "openai"
        api_key = "test-key"
        default_model = "gpt-4"
        
        [backends.bedrock]
        type = "bedrock"
        aws_profile = "default"
        aws_region = "us-east-1"
        """
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            
            assert config.default_backend == "openai"
            assert len(config.backends) == 2
            
            # Test OpenAI backend config
            openai_config = config.backends["openai"]
            assert openai_config.type == BackendType.OPENAI
            assert openai_config.api_key == "test-key"
            assert openai_config.default_model == "gpt-4"
            
            # Test Bedrock backend config
            bedrock_config = config.backends["bedrock"]
            assert bedrock_config.type == BackendType.BEDROCK
            assert bedrock_config.aws_profile == "default"
            assert bedrock_config.aws_region == "us-east-1"
            
        finally:
            os.unlink(config_path)
    
    def test_env_var_expansion(self):
        """Test environment variable expansion in configuration."""
        os.environ["TEST_API_KEY"] = "expanded-key"
        
        config_content = """
        [backends.openai]
        type = "openai"
        api_key = "$TEST_API_KEY"
        """
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            assert config.backends["openai"].api_key == "expanded-key"
            
        finally:
            os.unlink(config_path)
            if "TEST_API_KEY" in os.environ:
                del os.environ["TEST_API_KEY"]
    
    def test_missing_config_file(self):
        """Test error handling for missing configuration file."""
        with pytest.raises(ConfigurationError, match="not found"):
            load_config("/nonexistent/path/aiac.toml")
    
    def test_invalid_toml(self):
        """Test error handling for invalid TOML."""
        config_content = """
        [backends.openai
        type = "openai"
        """
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            with pytest.raises(ConfigurationError, match="Invalid TOML"):
                load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_get_backend_config(self):
        """Test getting backend configuration by name."""
        config = Config(
            backends={
                "openai": BackendType.OPENAI,
                "bedrock": BackendType.BEDROCK
            },
            default_backend="openai"
        )
        
        # Test getting specific backend
        name, backend_config = config.get_backend_config("bedrock")
        assert name == "bedrock"
        
        # Test getting default backend
        name, backend_config = config.get_backend_config(None)
        assert name == "openai"