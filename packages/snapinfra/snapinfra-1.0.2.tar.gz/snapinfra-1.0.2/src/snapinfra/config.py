"""Configuration management for SnapInfra."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from .config.loader import load_config as _load_config
from .config.models import Config as SnapInfraConfig


def load_config(config_path: Optional[str] = None) -> SnapInfraConfig:
    """Load configuration from file or environment variables."""
    try:
        return _load_config(config_path)
    except Exception:
        # Fallback to default config if loading fails
        from .config.models import Config
        return Config()


def save_config(config: SnapInfraConfig, config_path: str) -> None:
    """Save configuration to file."""
    # Simple implementation for now
    import json
    with open(config_path, 'w') as f:
        json.dump(config.model_dump(), f, indent=2)


__all__ = ['load_config', 'save_config', 'SnapInfraConfig']