"""Data models for AIAC."""

import re
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in an exchange between user and AI model."""
    
    role: str = Field(
        ...,
        description="The type of participant ('user' or 'assistant')"
    )
    content: str = Field(
        ...,
        description="The text content of the message"
    )


class Response(BaseModel):
    """Response from LLM API with extracted code."""
    
    full_output: str = Field(
        ...,
        description="Complete output returned by the API"
    )
    code: str = Field(
        ...,
        description="Extracted code section from the complete output"
    )
    api_key_used: str = Field(
        default="",
        description="API key used when making the request (for tracking)"
    )
    tokens_used: int = Field(
        default=0,
        description="Number of tokens utilized by the request"
    )
    stop_reason: str = Field(
        default="",
        description="Reason why the response ended"
    )
    
    @classmethod
    def create_from_output(
        cls, 
        output: str, 
        api_key: str = "",
        tokens_used: int = 0,
        stop_reason: str = ""
    ) -> "Response":
        """Create Response with extracted code from full output."""
        code = extract_code(output)
        if not code:
            code = output  # Fall back to full output if no code block found
            
        return cls(
            full_output=output,
            code=code,
            api_key_used=api_key,
            tokens_used=tokens_used,
            stop_reason=stop_reason
        )


# Code extraction regex matching Go implementation
CODE_REGEX = re.compile(r"(?ms)^```(?:[^\n]*)\n(.*?)\n```$")


def extract_code(output: str) -> Optional[str]:
    """
    Extract code block from markdown output.
    
    Matches the behavior of ExtractCode function from Go implementation.
    Returns the extracted code or None if no code block found.
    """
    match = CODE_REGEX.search(output)
    if match and match.group(1):
        return match.group(1)
    return None