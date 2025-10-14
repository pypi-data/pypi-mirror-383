"""Clipboard utility functions."""

import pyperclip
from rich.console import Console

console = Console()


def copy_to_clipboard(text: str) -> None:
    """
    Copy text to system clipboard.
    
    Args:
        text: Text to copy to clipboard
    """
    try:
        pyperclip.copy(text)
        console.print("✅ Generated code copied to clipboard.", style="green")
    except Exception as e:
        console.print(f"❌ Failed to copy to clipboard: {e}", style="red")