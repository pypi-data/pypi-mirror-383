"""Ollama backend implementation."""

from typing import Any, Dict, List, Optional

import httpx

from ..types import (
    Backend,
    Conversation,
    ErrRequestFailed,
    ErrUnexpectedStatus,
    Message,
    Response,
)


class OllamaConversation(Conversation):
    """Ollama conversation implementation."""
    
    def __init__(
        self,
        client: httpx.AsyncClient,
        model: str,
        initial_messages: List[Message]
    ):
        self._client = client
        self._model = model
        self._messages = initial_messages[:]
        self._extra_headers: Dict[str, str] = {}
        
    async def send(self, message: str) -> Response:
        """Send a message and get response from Ollama."""
        # Add user message to conversation
        user_message = Message(role="user", content=message)
        self._messages.append(user_message)
        
        # Prepare messages for Ollama API
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self._messages
        ]
        
        payload = {
            "model": self._model,
            "messages": api_messages,
            "stream": False,  # Get complete response at once
        }
        
        try:
            response = await self._client.post(
                "/chat",
                json=payload,
                headers=self._extra_headers
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise ErrUnexpectedStatus(response.status_code, error_text)
                
            data = response.json()
            
            if "message" not in data:
                raise ErrRequestFailed("No message in Ollama response")
                
            content = data["message"].get("content", "")
            if not content:
                raise ErrRequestFailed("Empty response from Ollama")
                
            # Add assistant response to conversation
            assistant_message = Message(role="assistant", content=content)
            self._messages.append(assistant_message)
            
            return Response.create_from_output(output=content)
            
        except httpx.RequestError as e:
            raise ErrRequestFailed(f"Network error: {e}") from e
        except Exception as e:
            if isinstance(e, (ErrRequestFailed, ErrUnexpectedStatus)):
                raise
            raise ErrRequestFailed(str(e)) from e
    
    def messages(self) -> List[Message]:
        """Get all messages in this conversation."""
        return self._messages[:]
    
    def add_header(self, key: str, value: str) -> None:
        """Add extra header for requests."""
        self._extra_headers[key] = value


class OllamaBackend(Backend):
    """Ollama backend implementation."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434/api",
        extra_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize Ollama backend.
        
        Args:
            base_url: Ollama API base URL 
            extra_headers: Extra headers to send with requests
        """
        self._base_url = base_url.rstrip("/")
        self._extra_headers = extra_headers or {}
        
        # Create HTTP client
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=60.0,
            headers=self._extra_headers
        )
        
    async def list_models(self) -> List[str]:
        """List available models from Ollama API."""
        try:
            response = await self._client.get("/tags")
            
            if response.status_code != 200:
                raise ErrUnexpectedStatus(
                    response.status_code, 
                    f"Failed to list models: {response.text}"
                )
                
            data = response.json()
            models = data.get("models", [])
            
            return [model["name"] for model in models]
            
        except httpx.RequestError as e:
            raise ErrRequestFailed(f"Network error: {e}") from e
        except Exception as e:
            if isinstance(e, (ErrRequestFailed, ErrUnexpectedStatus)):
                raise
            raise ErrRequestFailed(f"Failed to list models: {e}") from e
    
    def chat(self, model: str, *previous_messages: Message) -> Conversation:
        """Create a new conversation."""
        return OllamaConversation(
            client=self._client,
            model=model,
            initial_messages=list(previous_messages)
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()