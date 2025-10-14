"""Tests for data models."""

import pytest

from snapinfra.types.models import Message, Response, extract_code


class TestModels:
    """Test data models and utilities."""
    
    def test_message_model(self):
        """Test Message model validation."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
    
    def test_response_creation(self):
        """Test Response creation with code extraction."""
        full_output = """Here's your terraform code:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
}
```

This creates an EC2 instance."""
        
        response = Response.create_from_output(
            output=full_output,
            tokens_used=50,
            stop_reason="stop"
        )
        
        assert response.full_output == full_output
        assert "resource \"aws_instance\"" in response.code
        assert response.tokens_used == 50
        assert response.stop_reason == "stop"
    
    def test_extract_code_success(self):
        """Test successful code extraction."""
        markdown_text = """Here is your code:

```python
def hello():
    print("Hello, World!")
```

That's it!"""
        
        extracted = extract_code(markdown_text)
        assert extracted == 'def hello():\n    print("Hello, World!")'
    
    def test_extract_code_with_language(self):
        """Test code extraction with language specification."""
        markdown_text = """```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```"""
        
        extracted = extract_code(markdown_text)
        assert extracted == 'function greet(name) {\n    console.log(`Hello, ${name}!`);\n}'
    
    def test_extract_code_no_code_block(self):
        """Test code extraction when no code block exists."""
        text = "This is just plain text without any code blocks."
        extracted = extract_code(text)
        assert extracted is None
    
    def test_extract_code_empty_block(self):
        """Test code extraction with empty code block."""
        markdown_text = """```
```"""
        extracted = extract_code(markdown_text)
        assert extracted is None
        
    def test_extract_code_multiple_blocks(self):
        """Test code extraction with multiple blocks - should get first one."""
        markdown_text = """First block:
```python
print("first")
```

Second block:
```python
print("second")
```"""
        
        extracted = extract_code(markdown_text)
        assert extracted == 'print("first")'