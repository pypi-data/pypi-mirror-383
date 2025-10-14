"""Spinner utility for loading states."""

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.spinner import Spinner
from rich.status import Status

console = Console()


@contextmanager
def create_spinner(message: str = "Loading...") -> Generator[Status, None, None]:
    """
    Create a spinner context manager.
    
    Args:
        message: Message to display with the spinner
        
    Yields:
        Status object that can be used to update the spinner
    """
    with console.status(message, spinner="dots") as status:
        yield status