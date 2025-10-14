"""AIAC types and data structures."""

from .exceptions import (
    AiacError,
    BackendError,
    ConfigurationError,
    ErrNoDefaultBackend,
    ErrNoDefaultModel,
    ErrNoResults,
    ErrNoSuchBackend,
    ErrRequestFailed,
    ErrUnexpectedStatus,
)
from .interfaces import Backend, Conversation
from .models import Message, Response

__all__ = [
    # Exceptions
    "AiacError",
    "BackendError", 
    "ConfigurationError",
    "ErrNoDefaultBackend",
    "ErrNoDefaultModel",
    "ErrNoResults",
    "ErrNoSuchBackend",
    "ErrRequestFailed",
    "ErrUnexpectedStatus",
    # Interfaces
    "Backend",
    "Conversation", 
    # Models
    "Message",
    "Response",
]