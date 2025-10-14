"""Main CLI interface for SnapInfra."""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console

from ..backends import create_backend
from ..config import load_config
from ..config.loader import create_example_config, ensure_config_dir, get_default_config_path
from ..types import ConfigurationError, ErrNoDefaultModel
from ..utils import copy_to_clipboard
from ..utils.spinner import create_spinner
from .prompts import get_user_input, get_user_choice
from .interactive import start_interactive_mode, SnapInfraChat
from .startup import display_minimal_welcome, display_startup_sequence

console = Console()

# SnapInfra version
__version__ = "1.0.0"


@click.group(invoke_without_command=True)
@click.pass_context
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
    "-q", "--quiet",
    is_flag=True,
    help="Non-interactive mode, generate project and exit"
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
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Start interactive chat mode"
)
@click.argument("prompt", nargs=-1)
def main(
    ctx: click.Context,
    config: Optional[Path],
    backend: Optional[str],
    model: Optional[str],
    output_file: Optional[Path],
    quiet: bool,
    list_models: bool,
    timeout: int,
    version: bool,
    interactive: bool,
    prompt: tuple[str, ...]
) -> None:
    """
    SnapInfra - AI-Powered Enterprise Project Generator.
    
    Generate complete, production-ready projects with comprehensive infrastructure,
    backend APIs, frontend components, Docker deployment, testing, and documentation.
    
    🚀 Every command generates a COMPLETE PROJECT with:
    • 60+ production-ready files
    • Multi-cloud infrastructure (AWS, GCP, Azure)
    • Backend APIs with authentication
    • Database models and migrations
    • Docker deployment configurations
    • CI/CD pipelines and testing
    • Comprehensive API documentation
    • Deployment scripts for all platforms
    
    Projects are automatically saved to your choice of:
    • Current directory • Desktop • Custom path
    
    🔥 Interactive Mode (Default):
        snapinfra                    # Start interactive chat mode
        snapinfra -i                 # Explicit interactive mode
    
    ⚡ Direct Project Generation:
        snapinfra "todo app with REST API and React frontend"
        snapinfra "e-commerce platform with Node.js backend"
        snapinfra "blog website with Docker deployment"
        snapinfra "social media platform with authentication"
        snapinfra "inventory management system"
        snapinfra "real-time chat application"
        
    🎯 With Specific Backend:
        snapinfra -b groq "create full-stack chat application"
        snapinfra -b openai "blog platform with authentication"
        snapinfra -b claude "microservices architecture"
    """
    if version:
        console.print(f"snapinfra version {__version__}")
        return
    
    # Start interactive mode if requested
    if interactive:
        asyncio.run(start_interactive_mode())
        return
    
    # If no subcommand was invoked, run the original code generation logic
    if ctx.invoked_subcommand is not None:
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
    
    # If no prompt provided, start interactive mode  
    if not prompt:
        asyncio.run(start_interactive_mode())
        return
    
    # Clean up prompt (remove "get" or "generate" prefix for compatibility)
    prompt_list = list(prompt)
    if prompt_list[0].lower() in ("get", "generate"):
        prompt_list = prompt_list[1:]
    
    if not prompt_list:
        console.print("❌ Please provide a meaningful prompt", style="red")
        ctx.exit(1)
    
    # Build user input for comprehensive project generation
    user_input = ' '.join(prompt_list)
    
    # Always use comprehensive project generation - no single file generation
    try:
        asyncio.run(comprehensive_generate_command(
            config_obj=config_obj,
            backend_name=backend,
            model=model,
            user_prompt=user_input,
            output_file=output_file,
            quiet=quiet,
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


async def comprehensive_generate_command(
    config_obj,
    backend_name: Optional[str],
    model: Optional[str], 
    user_prompt: str,
    output_file: Optional[Path],
    quiet: bool,
    timeout: int
) -> None:
    """Generate comprehensive project using the SnapInfra project generation system."""
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
        
        # Create chat instance for comprehensive generation
        chat = SnapInfraChat()
        chat.backend = backend
        chat.current_model = model
        chat.current_backend_name = backend_name
        chat.config = config_obj
        
        console.print(f"🔍 Detected project description: {user_prompt}")
        console.print("🚀 Generating comprehensive project...")
        
        # Extract project name
        project_name = chat._extract_project_name(user_prompt)
        project_name = chat._sanitize_project_name(project_name)
        
        # Create project plan
        with create_spinner("Creating project plan...") as spinner:
            project_plan = await chat._create_project_plan(user_prompt, project_name)
            
        if not project_plan:
            console.print("❌ Failed to create project plan", style="red")
            return
            
        # Display project plan if not in quiet mode
        if not quiet:
            await chat._display_project_plan(project_plan)
            
            # Ask for confirmation in interactive mode
            if not get_user_choice("Proceed with comprehensive project generation?", default=True):
                console.print("🚫 Project generation cancelled", style="yellow")
                return
        
        # Determine output directory based on mode
        if quiet:
            # In quiet mode, use current directory by default
            if output_file:
                output_dir = str(output_file.parent / project_name)
            else:
                output_dir = f"./{project_name}"
        else:
            # In interactive mode, let user choose location
            output_dir = choose_output_location_cli(project_name)
            
        console.print(f"\n🏗️ Generating project at: {output_dir}")
        
        # Generate the complete project
        success = await chat._execute_project_generation(project_plan, output_dir)
        
        if success:
            console.print(f"\n🎉 Project '{project_name}' generated successfully!", style="bold green")
            console.print(f"📁 Location: {output_dir}")
            console.print(f"📦 Files created: {len(project_plan['files'])}")
            
            if not quiet:
                # Show next steps
                await chat._display_next_steps(output_dir, project_plan)
            else:
                # In quiet mode, just show basic next steps
                console.print(f"\n🚀 To get started:")
                console.print(f"  cd {output_dir}")
                if 'nodejs' in project_plan.get('tech_stack', []):
                    console.print(f"  npm install")
                if project_plan.get('docker_needed'):
                    console.print(f"  docker-compose up --build")
                console.print(f"  See README.md for detailed instructions")
        else:
            console.print("❌ Project generation failed", style="red")
            
    except Exception as e:
        console.print(f"❌ Comprehensive generation failed: {e}", style="red")
        raise


def choose_output_location_cli(project_name: str) -> str:
    """Let user choose where to save the generated project in CLI mode."""
    import os
    
    console.print(f"\n📁 Where would you like to save '{project_name}'?")
    
    # Get current directory
    current_option = f"./{project_name}"
    
    # Get desktop directory (Windows/macOS/Linux compatible)
    desktop_dir = None
    try:
        if os.name == 'nt':  # Windows
            desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop', project_name)
        else:  # macOS/Linux
            desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop', project_name)
            
            # Check if Desktop exists, fallback to home if not
            if not os.path.exists(os.path.dirname(desktop_dir)):
                desktop_dir = os.path.join(os.path.expanduser('~'), project_name)
    except Exception:
        desktop_dir = f"~/{project_name}"
    
    # Show options
    console.print(f"  1. Current directory: {current_option}")
    console.print(f"  2. Desktop: {desktop_dir}")
    console.print(f"  3. Custom path")
    console.print()
    
    while True:
        try:
            choice = get_user_choice(
                "Choose location [1/2/3]",
                valid_options=["1", "2", "3"]
            )
            
            if choice == "1":
                return current_option
            elif choice == "2":
                return desktop_dir
            elif choice == "3":
                custom_path = get_user_input(
                    f"Enter custom path for '{project_name}'",
                    default=f"./{project_name}"
                )
                # Ensure the project name is included in the path
                if custom_path and not custom_path.endswith(project_name):
                    custom_path = os.path.join(custom_path, project_name)
                return custom_path or current_option
                
        except (ValueError, KeyboardInterrupt):
            console.print("Invalid choice, please select 1, 2, or 3.", style="yellow")
            continue


# Removed single-file generation functions - SnapInfra now generates comprehensive projects only


def save_to_file(file_path: Path, content: str) -> None:
    """Save content to file."""
    try:
        file_path.write_text(content, encoding="utf-8")
        console.print(f"✅ Saved to {file_path}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to save {file_path}: {e}", style="red")


# Add diagram commands to the main group
# add_diagram_commands(main)

if __name__ == "__main__":
    main()
