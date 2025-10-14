"""Configuration file loading and parsing."""

import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from platformdirs import user_config_dir

from ..types.exceptions import ConfigurationError
from .models import Config


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.
    
    Uses XDG specification on Unix-like systems:
    - Linux/Unix: ~/.config/snapinfra/snapinfra.toml
    - Windows: %APPDATA%/snapinfra/snapinfra.toml  
    - macOS: ~/Library/Application Support/snapinfra/snapinfra.toml
    
    Returns:
        Path to the default configuration file
    """
    config_dir = Path(user_config_dir("snapinfra", "snapinfra"))
    return config_dir / "snapinfra.toml"


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load SnapInfra configuration from TOML file.
    
    Args:
        config_path: Path to configuration file, or None for default location
        
    Returns:
        Parsed configuration object
        
    Raises:
        ConfigurationError: If configuration cannot be loaded or parsed
    """
    if config_path is None:
        path = get_default_config_path()
    else:
        path = Path(config_path).expanduser().resolve()
        
    if not path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {path}\n"
            "Create a configuration file or specify a different path with --config"
        )
        
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigurationError(f"Invalid TOML in configuration file: {e}") from e
    except Exception as e:
        raise ConfigurationError(f"Failed to read configuration file: {e}") from e
        
    try:
        return Config.model_validate(data)
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration: {e}") from e


def create_example_config() -> str:
    """
    Create an example configuration file content.
    
    Returns:
        Example TOML configuration as a string
    """
    return '''# SnapInfra Configuration File
# Place this file at ~/.config/snapinfra/snapinfra.toml (or use --config to specify location)

default_backend = "openai"

[backends.openai]
type = "openai"
api_key = "$OPENAI_API_KEY"  # Environment variable
default_model = "gpt-4"

[backends.azure_openai]
type = "openai"
url = "https://your-tenant.openai.azure.com/openai/deployments/your-deployment"
api_key = "$AZURE_OPENAI_API_KEY"
api_version = "2023-05-15"
default_model = "gpt-4"

[backends.aws_bedrock]
type = "bedrock"
aws_profile = "default"
aws_region = "us-east-1"
default_model = "amazon.titan-text-express-v1"

[backends.local_ollama]
type = "ollama"
url = "http://localhost:11434/api"
default_model = "mistral:latest"

# Example with extra headers
[backends.custom_openai]
type = "openai"
url = "https://custom-openai-api.com/v1"
api_key = "your-api-key"
default_model = "gpt-3.5-turbo"

[backends.custom_openai.extra_headers]
"X-Custom-Header" = "custom-value"
"User-Agent" = "snapinfra-client"
'''


def ensure_config_dir() -> Path:
    """
    Ensure the configuration directory exists.
    
    Returns:
        Path to the configuration directory
    """
    config_dir = get_default_config_path().parent
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir