"""Abstract interfaces for AIAC backends."""

from abc import ABC, abstractmethod
from typing import List

from .models import Message, Response


class Conversation(ABC):
    """Interface for chat conversations with LLM backends."""
    
    @abstractmethod
    async def send(self, message: str) -> Response:
        """
        Send a message to the model and return the response.
        
        Args:
            message: The message to send to the model
            
        Returns:
            Response object containing the model's reply and metadata
        """
        pass
    
    @abstractmethod
    def messages(self) -> List[Message]:
        """
        Return all messages exchanged in this conversation.
        
        Returns:
            List of Message objects representing the conversation history
        """
        pass
    
    @abstractmethod
    def add_header(self, key: str, value: str) -> None:
        """
        Add an extra HTTP header for requests in this conversation.
        
        Args:
            key: Header name
            value: Header value
            
        Note:
            Not all providers support this (e.g., Bedrock doesn't)
        """
        pass


class Backend(ABC):
    """Interface that must be implemented for each LLM provider."""
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        Return a list of all models supported by this backend.
        
        Returns:
            List of model names available from this provider
        """
        pass
    
    @abstractmethod
    def chat(self, model: str, *previous_messages: Message) -> Conversation:
        """
        Initiate a conversation with an LLM backend.
        
        Args:
            model: Name of the model to use
            *previous_messages: Optional previous messages to load conversation context
            
        Returns:
            Conversation object for sending/receiving messages
        """
        pass