"""SnapInfra - Revolutionary AI-Powered Infrastructure Code Generator.

Transform natural language descriptions into production-ready infrastructure code,
architectural diagrams, and comprehensive documentation. Supports multiple IaC tools
and AI providers for maximum flexibility and power.

Key Features:
- Multi-provider AI support (OpenAI, Groq, AWS Bedrock, Ollama)
- Infrastructure-as-Code generation (Terraform, Kubernetes, Docker, etc.)
- Interactive refinement and chat-based iteration
- Automatic architecture diagram generation
- Production-ready templates with best practices
- Cross-platform compatibility (Windows, macOS, Linux)
"""

from .backends import create_backend
from .config import load_config
from .prompts import get_system_prompt
from .types import Backend, Conversation, Message, Response

__version__ = "1.0.3"

__all__ = [
    "__version__",
    "Backend",
    "Conversation",
    "Message", 
    "Response",
    "create_backend",
    "load_config",
    "get_system_prompt",
]
