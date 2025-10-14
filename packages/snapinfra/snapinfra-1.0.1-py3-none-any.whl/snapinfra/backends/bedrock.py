"""AWS Bedrock backend implementation."""

import json
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..types import (
    Backend,
    Conversation,
    ErrRequestFailed,
    ErrUnexpectedStatus,
    Message,
    Response,
)


class BedrockConversation(Conversation):
    """AWS Bedrock conversation implementation."""
    
    def __init__(
        self,
        client: boto3.client,
        model: str,
        initial_messages: List[Message]
    ):
        self._client = client
        self._model = model
        self._messages = initial_messages[:]
        
    async def send(self, message: str) -> Response:
        """Send a message and get response from Bedrock."""
        # Add user message to conversation
        user_message = Message(role="user", content=message)
        self._messages.append(user_message)
        
        try:
            # Prepare the request body based on the model
            if self._model.startswith("amazon.titan"):
                request_body = self._prepare_titan_request()
            elif self._model.startswith("anthropic.claude"):
                request_body = self._prepare_claude_request()
            elif self._model.startswith("ai21"):
                request_body = self._prepare_ai21_request()
            elif self._model.startswith("cohere"):
                request_body = self._prepare_cohere_request()
            else:
                # Default format - try Anthropic Claude format
                request_body = self._prepare_claude_request()
            
            # Make the API call
            response = self._client.invoke_model(
                modelId=self._model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            content = self._extract_content(response_body)
            
            if not content:
                raise ErrRequestFailed("Empty response from Bedrock")
            
            # Add assistant response to conversation
            assistant_message = Message(role="assistant", content=content)
            self._messages.append(assistant_message)
            
            return Response.create_from_output(output=content)
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise ErrRequestFailed(f"[{error_code}]: {error_message}") from e
        except BotoCoreError as e:
            raise ErrRequestFailed(f"AWS SDK error: {e}") from e
        except Exception as e:
            if isinstance(e, ErrRequestFailed):
                raise
            raise ErrRequestFailed(str(e)) from e
    
    def _prepare_titan_request(self) -> Dict[str, Any]:
        """Prepare request for Amazon Titan models."""
        prompt = self._build_prompt_string()
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
    
    def _prepare_claude_request(self) -> Dict[str, Any]:
        """Prepare request for Anthropic Claude models."""
        prompt = self._build_claude_prompt()
        return {
            "prompt": prompt,
            "max_tokens_to_sample": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop_sequences": ["\\n\\nHuman:"]
        }
    
    def _prepare_ai21_request(self) -> Dict[str, Any]:
        """Prepare request for AI21 models."""
        prompt = self._build_prompt_string()
        return {
            "prompt": prompt,
            "maxTokens": 4096,
            "temperature": 0.7,
            "topP": 0.9
        }
    
    def _prepare_cohere_request(self) -> Dict[str, Any]:
        """Prepare request for Cohere models."""
        prompt = self._build_prompt_string()
        return {
            "prompt": prompt,
            "max_tokens": 4096,
            "temperature": 0.7,
            "p": 0.9
        }
    
    def _build_prompt_string(self) -> str:
        """Build a simple prompt string from messages."""
        parts = []
        for msg in self._messages:
            role = "Human" if msg.role == "user" else "Assistant"
            parts.append(f"{role}: {msg.content}")
        return "\\n\\n".join(parts) + "\\n\\nAssistant:"
    
    def _build_claude_prompt(self) -> str:
        """Build Claude-specific prompt format."""
        parts = []
        for msg in self._messages:
            if msg.role == "user":
                parts.append(f"\\n\\nHuman: {msg.content}")
            else:
                parts.append(f"\\n\\nAssistant: {msg.content}")
        return "".join(parts) + "\\n\\nAssistant:"
    
    def _extract_content(self, response_body: Dict[str, Any]) -> str:
        """Extract content from response body based on model type."""
        if self._model.startswith("amazon.titan"):
            results = response_body.get("results", [])
            if results:
                return results[0].get("outputText", "")
        elif self._model.startswith("anthropic.claude"):
            return response_body.get("completion", "")
        elif self._model.startswith("ai21"):
            completions = response_body.get("completions", [])
            if completions:
                return completions[0].get("data", {}).get("text", "")
        elif self._model.startswith("cohere"):
            generations = response_body.get("generations", [])
            if generations:
                return generations[0].get("text", "")
        
        # Fallback - try common fields
        return (
            response_body.get("completion") or
            response_body.get("outputText") or
            response_body.get("text") or
            ""
        )
    
    def messages(self) -> List[Message]:
        """Get all messages in this conversation."""
        return self._messages[:]
    
    def add_header(self, key: str, value: str) -> None:
        """Add extra header for requests. Not supported by Bedrock."""
        # Bedrock doesn't support custom headers, so this is a no-op
        pass


class BedrockBackend(Backend):
    """AWS Bedrock backend implementation."""
    
    def __init__(
        self,
        aws_profile: Optional[str] = None,
        aws_region: str = "us-east-1"
    ):
        """
        Initialize Bedrock backend.
        
        Args:
            aws_profile: AWS profile name
            aws_region: AWS region 
        """
        self._aws_profile = aws_profile
        self._aws_region = aws_region
        
        # Create boto3 session and client
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
        else:
            session = boto3.Session()
            
        self._client = session.client(
            "bedrock-runtime",
            region_name=aws_region
        )
        
    async def list_models(self) -> List[str]:
        """List available models from Bedrock."""
        try:
            # Create a regular Bedrock client for listing models
            if self._aws_profile:
                session = boto3.Session(profile_name=self._aws_profile)
            else:
                session = boto3.Session()
                
            bedrock_client = session.client(
                "bedrock", 
                region_name=self._aws_region
            )
            
            response = bedrock_client.list_foundation_models()
            models = []
            
            for model in response.get("modelSummaries", []):
                model_id = model.get("modelId")
                if model_id:
                    models.append(model_id)
                    
            return models
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise ErrRequestFailed(f"[{error_code}]: {error_message}") from e
        except Exception as e:
            raise ErrRequestFailed(f"Failed to list models: {e}") from e
    
    def chat(self, model: str, *previous_messages: Message) -> Conversation:
        """Create a new conversation."""
        return BedrockConversation(
            client=self._client,
            model=model,
            initial_messages=list(previous_messages)
        )