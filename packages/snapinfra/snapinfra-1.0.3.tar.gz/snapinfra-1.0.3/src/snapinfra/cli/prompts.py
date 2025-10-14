"""Interactive prompt utilities for CLI."""

from typing import List, Optional

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def get_user_input(label: str, default: str = "") -> str:
    """
    Get user input with a prompt.
    
    Args:
        label: Prompt label
        default: Default value
        
    Returns:
        User input string
    """
    try:
        return Prompt.ask(label, default=default)
    except (KeyboardInterrupt, EOFError):
        return ""


def get_user_choice(
    question: str, 
    valid_options: Optional[List[str]] = None,
    default: Optional[bool] = None
) -> str:
    """
    Get user choice with validation.
    
    Args:
        question: Question to ask
        valid_options: List of valid single-character options
        default: Default boolean value (for yes/no questions)
        
    Returns:
        User choice as lowercase string
    """
    if valid_options:
        # Multiple choice question
        while True:
            try:
                answer = Prompt.ask(question).lower().strip()
                if answer in valid_options:
                    return answer
                console.print(f"❌ Invalid input. Please choose from: {', '.join(valid_options)}", style="red")
            except (KeyboardInterrupt, EOFError):
                return "q"  # Default to quit
    else:
        # Yes/no question
        try:
            return "y" if Confirm.ask(question, default=default) else "n"
        except (KeyboardInterrupt, EOFError):
            return "n"