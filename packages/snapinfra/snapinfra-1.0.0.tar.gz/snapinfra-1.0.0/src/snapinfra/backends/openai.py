"""OpenAI backend implementation."""

import asyncio
from typing import Dict, List, Optional

import httpx
from openai import AsyncOpenAI

from ..types import Backend, Conversation, ErrRequestFailed, Message, Response


class OpenAIConversation(Conversation):
    """OpenAI conversation implementation."""
    
    def __init__(
        self, 
        client: AsyncOpenAI,
        model: str,
        initial_messages: List[Message]
    ):
        self._client = client
        self._model = model
        self._messages = initial_messages[:]
        self._extra_headers: Dict[str, str] = {}
        
    async def send(self, message: str) -> Response:
        """Send a message and get response from OpenAI."""
        # Add user message to conversation
        user_message = Message(role="user", content=message)
        self._messages.append(user_message)
        
        # Prepare messages for OpenAI API
        api_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in self._messages
        ]
        
        try:
            # Make API call with extra headers
            extra_headers = self._extra_headers or {}
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=api_messages,
                extra_headers=extra_headers
            )
            
            if not response.choices:
                raise ErrRequestFailed("No choices returned from OpenAI API")
                
            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                raise ErrRequestFailed("Empty response from OpenAI API")
                
            content = choice.message.content
            
            # Add assistant response to conversation
            assistant_message = Message(role="assistant", content=content)
            self._messages.append(assistant_message)
            
            # Extract token usage and other metadata
            tokens_used = response.usage.total_tokens if response.usage else 0
            stop_reason = choice.finish_reason or ""
            
            return Response.create_from_output(
                output=content,
                tokens_used=tokens_used,
                stop_reason=stop_reason
            )
            
        except Exception as e:
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                # OpenAI API error with detailed response
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg = error_data['error'].get('message', str(e))
                    error_type = error_data['error'].get('type', 'unknown')
                    raise ErrRequestFailed(f"[{error_type}]: {error_msg}") from e
            
            raise ErrRequestFailed(str(e)) from e
    
    def messages(self) -> List[Message]:
        """Get all messages in this conversation."""
        return self._messages[:]
    
    def add_header(self, key: str, value: str) -> None:
        """Add extra header for requests."""
        self._extra_headers[key] = value


class OpenAIBackend(Backend):
    """OpenAI backend implementation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize OpenAI backend.
        
        Args:
            api_key: OpenAI API key
            base_url: Custom API base URL (for Azure OpenAI, etc.)
            api_version: API version for Azure OpenAI
            extra_headers: Extra headers to send with requests
        """
        self._api_key = api_key
        self._base_url = base_url or "https://api.openai.com/v1"
        self._api_version = api_version
        self._extra_headers = extra_headers or {}
        
        # Handle Azure OpenAI authentication
        default_headers = {}
        if base_url and ".openai.azure.com" in base_url:
            # Azure OpenAI uses api-key header
            if api_key:
                default_headers["api-key"] = api_key
            # Set api_key to None so OpenAI client doesn't add Authorization header
            client_api_key = None
        else:
            # Standard OpenAI API uses Authorization: Bearer
            client_api_key = api_key
            
        # Merge with extra headers
        default_headers.update(self._extra_headers)
        
        # Create async OpenAI client
        self._client = AsyncOpenAI(
            api_key=client_api_key,
            base_url=self._base_url,
            default_headers=default_headers if default_headers else None,
            timeout=60.0,
        )
        
    async def list_models(self) -> List[str]:
        """List available models from OpenAI API."""
        try:
            models = await self._client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            raise ErrRequestFailed(f"Failed to list models: {e}") from e
    
    def chat(self, model: str, *previous_messages: Message) -> Conversation:
        """Create a new conversation."""
        return OpenAIConversation(
            client=self._client,
            model=model,
            initial_messages=list(previous_messages)
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.close()