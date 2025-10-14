"""Groq backend implementation."""

from typing import Dict, List, Optional

from groq import AsyncGroq

from ..types import Backend, Conversation, ErrRequestFailed, Message, Response


class GroqConversation(Conversation):
    """Groq conversation implementation."""
    
    def __init__(
        self, 
        client: AsyncGroq,
        model: str,
        initial_messages: List[Message],
        response_format: Optional[Dict] = None
    ):
        self._client = client
        self._model = model
        self._messages = initial_messages[:]
        self._extra_headers: Dict[str, str] = {}
        self._response_format = response_format
        
    async def send(self, message: str) -> Response:
        """Send a message and get response from Groq."""
        # Add user message to conversation
        user_message = Message(role="user", content=message)
        self._messages.append(user_message)
        
        # Prepare messages for Groq API
        api_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in self._messages
        ]
        
        try:
            # Prepare API call parameters
            api_params = {
                "model": self._model,
                "messages": api_messages,
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1,
            }
            
            # Add response format if specified
            if self._response_format:
                api_params["response_format"] = self._response_format
                
            # Make API call
            response = await self._client.chat.completions.create(**api_params)
            
            if not response.choices:
                raise ErrRequestFailed("No choices returned from Groq API")
                
            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                raise ErrRequestFailed("Empty response from Groq API")
                
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
                # Groq API error with detailed response
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', str(e))
                        error_type = error_data['error'].get('type', 'unknown')
                        raise ErrRequestFailed(f"[{error_type}]: {error_msg}") from e
                except Exception:
                    pass
            
            raise ErrRequestFailed(str(e)) from e
    
    def messages(self) -> List[Message]:
        """Get all messages in this conversation."""
        return self._messages[:]
    
    def add_header(self, key: str, value: str) -> None:
        """Add extra header for requests."""
        self._extra_headers[key] = value


class GroqBackend(Backend):
    """Groq backend implementation."""
    
    # Popular Groq models including the latest ones
    SUPPORTED_MODELS = [
        "meta-llama/llama-4-scout-17b-16e-instruct",  # Latest Llama model
        "meta-llama/llama-3.2-90b-text-preview",
        "meta-llama/llama-3.2-11b-text-preview", 
        "meta-llama/llama-3.2-3b-preview",
        "meta-llama/llama-3.2-1b-preview",
        "meta-llama/llama-3.1-70b-versatile",
        "meta-llama/llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
        "llava-v1.5-7b-4096-preview",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        response_format: Optional[Dict] = None
    ):
        """
        Initialize Groq backend.
        
        Args:
            api_key: Groq API key
            base_url: Custom API base URL (optional)
            extra_headers: Extra headers to send with requests
            response_format: Response format (e.g., {"type": "json_object"})
        """
        self._api_key = api_key
        self._base_url = base_url or "https://api.groq.com/openai/v1"
        self._extra_headers = extra_headers or {}
        self._response_format = response_format
        
        # Create async Groq client
        client_params = {
            "api_key": api_key,
            "timeout": 60.0,
        }
        
        if base_url:
            client_params["base_url"] = base_url
            
        self._client = AsyncGroq(**client_params)
        
    async def list_models(self) -> List[str]:
        """List available models from Groq API."""
        try:
            models = await self._client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            # Fall back to known supported models if API call fails
            return self.SUPPORTED_MODELS
    
    def chat(self, model: str, *previous_messages: Message) -> Conversation:
        """Create a new conversation."""
        return GroqConversation(
            client=self._client,
            model=model,
            initial_messages=list(previous_messages),
            response_format=self._response_format
        )
        
    def set_response_format(self, response_format: Optional[Dict] = None) -> None:
        """Set the response format for future conversations."""
        self._response_format = response_format
        
    def set_json_mode(self, enabled: bool = True) -> None:
        """Enable or disable JSON response mode."""
        if enabled:
            self._response_format = {"type": "json_object"}
        else:
            self._response_format = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.close()