"""Main CLI interface for SnapInfra."""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.syntax import Syntax

from ..backends import create_backend
from ..config import load_config
from ..config.loader import create_example_config, ensure_config_dir, get_default_config_path
from ..prompts.prompt_builder import build_enhanced_prompt
from ..types import ConfigurationError, ErrNoDefaultModel, Message
from ..utils import copy_to_clipboard, create_spinner
from .prompts import get_user_choice, get_user_input

console = Console()

# SnapInfra version
__version__ = "1.0.0"


@click.command()
@click.option(
    "-c", "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path"
)
@click.option(
    "-b", "--backend",
    help="Backend to use"
)
@click.option(
    "-m", "--model", 
    help="Model to use"
)
@click.option(
    "-o", "--output-file",
    type=click.Path(path_type=Path),
    help="Output file to save generated code"
)
@click.option(
    "-r", "--readme-file",
    type=click.Path(path_type=Path), 
    help="Readme file to save full Markdown output"
)
@click.option(
    "-q", "--quiet",
    is_flag=True,
    help="Non-interactive mode, print/save output and exit"
)
@click.option(
    "-f", "--full",
    is_flag=True,
    help="Print full Markdown output to stdout"
)
@click.option(
    "--clipboard",
    is_flag=True,
    help="Copy generated code to clipboard (in --quiet mode)"
)
@click.option(
    "--list-models",
    is_flag=True,
    help="List supported models and exit"
)
@click.option(
    "--timeout",
    type=int,
    default=60,
    help="Timeout to generate code, in seconds"
)
@click.option(
    "--version",
    is_flag=True,
    help="Print snapinfra version and exit"
)
@click.argument("prompt", nargs=-1)
@click.pass_context
def main(
    ctx: click.Context,
    config: Optional[Path],
    backend: Optional[str],
    model: Optional[str],
    output_file: Optional[Path],
    readme_file: Optional[Path],
    quiet: bool,
    full: bool,
    clipboard: bool,
    list_models: bool,
    timeout: int,
    version: bool,
    prompt: tuple[str, ...]
) -> None:
    """
    SnapInfra - AI-Powered Infrastructure Code Generator.
    
    Generate IaC templates, configurations, utilities, and more via LLM providers
    such as OpenAI, Amazon Bedrock, and Ollama.
    
    Examples:
        snapinfra terraform for a highly available eks
        snapinfra pulumi golang for an s3 with sns notification
        snapinfra dockerfile for a secured nginx
        snapinfra k8s manifest for a mongodb deployment
    """
    if version:
        console.print(f"snapinfra version {__version__}")
        return
    
    # Handle configuration setup
    try:
        config_obj = load_config(str(config) if config else None)
    except ConfigurationError as e:
        if "not found" in str(e):
            handle_missing_config()
            return
        console.print(f"❌ Configuration error: {e}", style="red")
        ctx.exit(1)
    except Exception as e:
        console.print(f"❌ Failed to load configuration: {e}", style="red")
        ctx.exit(1)
    
    # List models if requested
    if list_models:
        asyncio.run(list_models_command(config_obj, backend))
        return
    
    # Validate prompt
    if not prompt:
        console.print("❌ Please provide a prompt", style="red")
        console.print("\\nExample: snapinfra terraform for AWS EC2")
        ctx.exit(1)
    
    # Clean up prompt (remove "get" or "generate" prefix for compatibility)
    prompt_list = list(prompt)
    if prompt_list[0].lower() in ("get", "generate"):
        prompt_list = prompt_list[1:]
    
    if not prompt_list:
        console.print("❌ Please provide a meaningful prompt", style="red")
        ctx.exit(1)
    
    # Build enhanced prompt with system message
    user_input = ' '.join(prompt_list)
    include_explanations = bool(readme_file or full)
    system_prompt, enhanced_prompt = build_enhanced_prompt(user_input, include_explanations)
    
    # Run code generation
    try:
        asyncio.run(generate_code_command(
            config_obj=config_obj,
            backend_name=backend,
            model=model,
            system_prompt=system_prompt,
            user_prompt=enhanced_prompt,
            output_file=output_file,
            readme_file=readme_file,
            quiet=quiet,
            full=full,
            clipboard=clipboard,
            timeout=timeout
        ))
    except KeyboardInterrupt:
        console.print("\\n⚠️  Interrupted by user", style="yellow")
        ctx.exit(130)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        ctx.exit(1)


def handle_missing_config() -> None:
    """Handle missing configuration file by offering to create one."""
    console.print("📋 Configuration file not found.", style="yellow")
    console.print("\\nSnapInfra needs a configuration file to connect to LLM providers.")
    
    if get_user_choice("Would you like to create an example configuration file?"):
        try:
            config_dir = ensure_config_dir()
            config_path = get_default_config_path()
            
            with open(config_path, "w") as f:
                f.write(create_example_config())
                
            console.print(f"✅ Created example configuration at: {config_path}", style="green")
            console.print("\\n📝 Please edit the configuration file to add your API keys and settings.")
            console.print("\\nThen run snapinfra again with your prompt.")
            
        except Exception as e:
            console.print(f"❌ Failed to create configuration: {e}", style="red")


async def list_models_command(config_obj, backend_name: Optional[str]) -> None:
    """List available models for the specified backend."""
    try:
        backend_name, backend_config = config_obj.get_backend_config(backend_name)
        backend = create_backend(backend_config)
        
        with create_spinner(f"🔍 Fetching models from {backend_name}...") as spinner:
            models = await backend.list_models()
            
        if models:
            console.print(f"\\n📋 Available models for '{backend_name}':", style="bold")
            for model in models:
                console.print(f"  • {model}")
        else:
            console.print("ℹ️  No models found", style="yellow")
            
    except Exception as e:
        console.print(f"❌ Failed to list models: {e}", style="red")
        sys.exit(1)


async def generate_code_command(
    config_obj,
    backend_name: Optional[str],
    model: Optional[str],
    system_prompt: str,
    user_prompt: str,
    output_file: Optional[Path],
    readme_file: Optional[Path],
    quiet: bool,
    full: bool,
    clipboard: bool,
    timeout: int
) -> None:
    """Generate code using the specified configuration."""
    try:
        # Get backend configuration
        backend_name, backend_config = config_obj.get_backend_config(backend_name)
        backend = create_backend(backend_config)
        
        # Determine model to use
        if not model:
            if backend_config.default_model:
                model = backend_config.default_model
            else:
                raise ErrNoDefaultModel()
        
        # Create conversation with system prompt
        system_message = Message(role="system", content=system_prompt)
        conversation = backend.chat(model, system_message)
        
        # Generate code with timeout
        with create_spinner("🤖 Generating code...") as spinner:
            try:
                response = await asyncio.wait_for(
                    conversation.send(user_prompt), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                console.print(f"❌ Generation timed out after {timeout} seconds", style="red")
                return
        
        # Determine what to display
        display_content = response.full_output if full else response.code
        
        # Quiet mode - just output and optionally save/copy
        if quiet:
            console.print(display_content)
            
            if clipboard:
                copy_to_clipboard(display_content)
            
            if output_file:
                save_to_file(output_file, response.code)
            
            if readme_file:
                save_to_file(readme_file, response.full_output)
                
            return
        
        # Interactive mode
        await interactive_mode(response, output_file, readme_file, full, conversation)
        
    except Exception as e:
        console.print(f"❌ Generation failed: {e}", style="red")
        raise


async def interactive_mode(response, output_file, readme_file, full, conversation):
    """Handle interactive mode with conversation options."""
    display_content = response.full_output if full else response.code
    
    # Display generated code with syntax highlighting
    if response.code != response.full_output:
        # Try to detect language for syntax highlighting
        syntax = Syntax(response.code, "text", theme="monokai", line_numbers=True)
        console.print("\\n✨ Generated Code:", style="bold green")
        console.print(syntax)
    else:
        console.print("\\n✨ Generated Output:", style="bold green")
        console.print(display_content)
    
    while True:
        console.print("\\n📋 Options:")
        options = [
            ("s", "save and exit"),
            ("w", "save and chat"),
            ("c", "continue chatting"),
            ("r", "retry same prompt"),
            ("y", "copy to clipboard"),
            ("q", "quit")
        ]
        
        for key, desc in options:
            console.print(f"  [{key.upper()}/{key}]: {desc}")
        
        choice = get_user_choice("Choice", valid_options=[opt[0] for opt in options])
        
        if choice == "q":
            break
        elif choice == "y":
            copy_to_clipboard(response.code)
        elif choice == "s":
            save_output(output_file, readme_file, response)
            break
        elif choice == "w":
            save_output(output_file, readme_file, response)
            # Fall through to continue chatting
            choice = "c"
        elif choice == "r":
            # Retry with the same prompt
            console.print("🔄 Retrying...")
            # This would need the original prompt, which we'd need to pass in
            pass
            
        if choice == "c":
            new_message = get_user_input("New message")
            if new_message:
                with create_spinner("🤖 Generating response..."):
                    response = await conversation.send(new_message)
                
                # Display new response
                display_content = response.full_output if full else response.code
                console.print("\\n✨ AI Response:", style="bold blue")
                console.print(display_content)


def save_output(output_file: Optional[Path], readme_file: Optional[Path], response) -> None:
    """Save output to files."""
    # Ask for output file if not provided
    if not output_file:
        filename = get_user_input("Enter file path for generated code")
        if filename:
            output_file = Path(filename)
    
    # Ask for readme file if not provided
    if not readme_file:
        filename = get_user_input("Enter file path for full output, or leave empty to ignore")
        if filename:
            readme_file = Path(filename)
    
    # Save files
    if output_file:
        save_to_file(output_file, response.code)
    
    if readme_file:
        save_to_file(readme_file, response.full_output)


def save_to_file(file_path: Path, content: str) -> None:
    """Save content to file."""
    try:
        file_path.write_text(content, encoding="utf-8")
        console.print(f"✅ Saved to {file_path}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to save {file_path}: {e}", style="red")


if __name__ == "__main__":
    main()