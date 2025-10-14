"""Interactive chat interface for SnapInfra CLI."""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.box import ROUNDED, HEAVY, SIMPLE, SQUARE

from ..backends import create_backend
from ..config import load_config
from ..prompts.prompt_builder import build_enhanced_prompt
from ..types import Message, ConfigurationError
from ..utils import copy_to_clipboard
from ..utils.model_switching import model_switcher
from .startup import display_minimal_welcome, display_startup_sequence

console = Console()

class SnapInfraChat:
    """Interactive chat interface for SnapInfra."""
    
    def __init__(self):
        self.config = None
        self.backend = None
        self.conversation = None
        self.chat_history: List[Dict[str, Any]] = []
        self.current_model = None
        self.current_backend_name = None
        self.project_mode = True  # Default to project generation mode
        
        # Model switching for rate limit handling
        self.original_model = None
        self.original_backend_name = None
        self.fallback_models = []
        self.current_fallback_index = 0
        self.model_switches_count = 0
        
    # Removed old display_welcome method - using startup.py display_minimal_welcome instead
    
    def display_configuration_status(self) -> None:
        """Display current configuration status."""
        if not self.config:
            return
            
        # Backend status
        backends_table = Table(title="Available AI Backends", box=ROUNDED, show_header=True, header_style="bold #0088FF")
        backends_table.add_column("Backend", style="#0088FF", no_wrap=True)
        backends_table.add_column("Status", no_wrap=True)
        backends_table.add_column("Default Model", style="white")
        
        for backend_name, backend_config in self.config.backends.items():
            status = "Ready" if backend_config.api_key else "API Key Required"
            status_style = "bold green" if backend_config.api_key else "bold red"
            model = backend_config.default_model or "Not configured"
            
            # Highlight current backend
            name_style = "bold #0088FF" if backend_name == self.current_backend_name else "#0088FF"
            backends_table.add_row(
                Text(backend_name, style=name_style),
                Text(status, style=status_style),
                model
            )
        
        console.print(backends_table)
        console.print()
        
        # Current session info
        if self.current_backend_name and self.current_model:
            session_info = Panel(
                Text.assemble(
                    ("🎯 Active Session\n", "bold green"),
                    ("Backend: ", "white"), (self.current_backend_name, "bold cyan"),
                    ("  Model: ", "white"), (self.current_model, "bold yellow")
                ),
                border_style="green",
                width=50
            )
            console.print(Align.center(session_info))
            console.print()

    def display_active_session(self) -> None:
        """Display just the active session info."""
        if self.current_backend_name and self.current_model:
            console.print(f"Active: {self.current_backend_name.upper()} | {self.current_model}", style="#0088FF")
            console.print()

    def display_chat_header(self) -> None:
        """Display clean chat header with session info only (no logo)."""
        # Show active session info
        if self.current_backend_name and self.current_model:
            console.print(f"Active: {self.current_backend_name.upper()} | {self.current_model} | Mode: SnapInfra Agentic Generation\\n", style="#0088FF")

    def display_quick_commands(self) -> None:
        """Display quick command reference."""
        commands_table = Table(title="⚡ Quick Commands", box=SIMPLE, show_header=False)
        commands_table.add_column("Command", style="bold cyan", no_wrap=True)
        commands_table.add_column("Description", style="white")
        
        commands = [
            ("/help", "Show help and tips"),
            ("/models", "List available models"),
            ("/switch", "Switch backend or model"),
            ("/keys", "Manage API keys (add, delete, view)"),
            ("/save", "Save last response to file"),
            ("/copy", "Copy last response to clipboard"),
            ("/clear", "Clear conversation history"),
            ("/history", "Show conversation history"),
            ("/examples", "Show example project prompts"),
            ("/exit", "Exit SnapInfra")
        ]
        
        console.print("\n💡 Note: Describe any project idea and get a complete working project generated instantly!", style="#0088FF")
        
        for cmd, desc in commands:
            commands_table.add_row(cmd, desc)
        
        console.print(commands_table)
        console.print()

    async def setup_configuration(self) -> bool:
        """Setup and validate configuration with API keys."""
        try:
            self.config = load_config()
            
            # Check if any backend has a valid API key (not empty, not unresolved env var)
            has_api_keys = any(
                backend_config.api_key and 
                backend_config.api_key.strip() and 
                not backend_config.api_key.startswith('$') and  # Reject unresolved env vars
                backend_config.api_key not in ['your-api-key', 'None']  # Reject placeholders
                for backend_config in self.config.backends.values()
            )
            
            if not has_api_keys:
                # Prompt user to set up API keys interactively
                if await self.interactive_api_key_setup():
                    # Reload config after setup
                    self.config = load_config()
                    # Check for deprecated models after setup
                    await self.update_deprecated_models()
                    return True
                else:
                    return False
            
            # Check for deprecated models in existing configuration
            await self.update_deprecated_models()
            return True
            
        except ConfigurationError as e:
            if "not found" in str(e):
                console.print(Panel(
                    Text.assemble(
                        ("Configuration Setup Required\n\n", "bold #0088FF"),
                        ("SnapInfra needs a config file to connect to AI providers.\n", "white"),
                        ("Want to create one now?", "bold white")
                    ),
                    title="Setup",
                    border_style="#0088FF",
                    box=SQUARE
                ))
                
                if Confirm.ask("Create config file?", default=True):
                    from ..config.loader import create_example_config, ensure_config_dir, get_default_config_path
                    
                    try:
                        config_dir = ensure_config_dir()
                        config_path = get_default_config_path()
                        
                        with open(config_path, "w") as f:
                            f.write(create_example_config())
                        
                        console.print(Panel(
                            Text.assemble(
                                ("Config file created at:\n", "bold green"),
                                (str(config_path), "bold white"),
                                ("\n\nNow let's configure your API keys!", "#0088FF")
                            ),
                            title="Config Created",
                            border_style="green",
                            box=SQUARE
                        ))
                        console.print()
                        
                        # Load the new config and setup API keys interactively
                        self.config = load_config()
                        if await self.interactive_api_key_setup():
                            # Reload config after setup
                            self.config = load_config()
                            return True
                        else:
                            return False
                    except Exception as e:
                        console.print(f"❌ Failed to create configuration: {e}", style="red")
                        return False
                else:
                    return False
            else:
                console.print(f"❌ Configuration error: {e}", style="red")
                return False

    async def interactive_api_key_setup(self) -> bool:
        """Interactive setup of API keys for available backends."""
        console.print(Panel(
            Text.assemble(
                ("🔑 API Key Setup\n\n", "bold #0088FF"),
                ("Let's configure your AI provider API keys.\n", "white"),
                ("You can set up one or more providers to get started.", "white")
            ),
            title="Setup Required",
            border_style="#0088FF",
            box=SQUARE
        ))
        console.print()
        
        # Available backend options for setup
        backend_options = [
            ("openai", "OpenAI (GPT-4, GPT-3.5-turbo, etc.)", "OPENAI_API_KEY"),
            ("groq", "Groq (Fast inference, Mixtral, Llama)", "GROQ_API_KEY"),
            ("azure_openai", "Azure OpenAI (Enterprise OpenAI)", "AZURE_OPENAI_API_KEY"),
        ]
        
        # Show available options
        console.print("📋 Available AI Providers:")
        for i, (backend_name, description, env_var) in enumerate(backend_options, 1):
            console.print(f"  {i}. {description}")
        console.print()
        
        configured_any = False
        
        # Let user configure backends
        while True:
            try:
                choice = Prompt.ask(
                    "Select provider to configure (1-3) or 'done' to finish",
                    default="1"
                )
                
                if choice.lower() == 'done':
                    break
                    
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(backend_options):
                    backend_name, description, env_var = backend_options[choice_idx]
                    
                    console.print(f"\n🔧 Configuring {description}")
                    
                    # Get API key from user
                    api_key = Prompt.ask(
                        f"Enter your {backend_name.upper()} API key",
                        password=True  # Hide the input
                    )
                    
                    if api_key and api_key.strip():
                        # Save API key to config
                        if await self.save_api_key_to_config(backend_name, api_key.strip()):
                            console.print(f"✅ {backend_name.upper()} API key configured successfully!", style="green")
                            configured_any = True
                        else:
                            console.print(f"❌ Failed to save {backend_name.upper()} API key", style="red")
                    else:
                        console.print("⚠️ Empty API key, skipping...", style="yellow")
                        
                    console.print()
                else:
                    console.print("Invalid choice, please try again.", style="red")
                    
            except ValueError:
                if choice.lower() != 'done':
                    console.print("Invalid choice, please try again.", style="red")
                    
        if configured_any:
            console.print(Panel(
                Text.assemble(
                    ("🎉 Setup Complete!\n\n", "bold green"),
                    ("Your API keys have been configured.\n", "white"),
                    ("You can now start using SnapInfra!", "bold white")
                ),
                title="Success",
                border_style="green",
                box=SQUARE
            ))
            return True
        else:
            console.print(Panel(
                Text.assemble(
                    ("⚠️ No API Keys Configured\n\n", "bold yellow"),
                    ("You need at least one API key to use SnapInfra.\n", "white"),
                    ("You can run the setup again anytime.", "white")
                ),
                title="Setup Incomplete",
                border_style="yellow",
                box=SQUARE
            ))
            return False
            
    async def save_api_key_to_config(self, backend_name: str, api_key: str) -> bool:
        """Save an API key to the configuration file."""
        try:
            from ..config.loader import get_default_config_path
            import toml
            
            config_path = get_default_config_path()
            
            # Read existing config
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = toml.load(f)
            else:
                config_data = {}
            
            # Ensure backends section exists
            if 'backends' not in config_data:
                config_data['backends'] = {}
            
            # Ensure the specific backend section exists
            if backend_name not in config_data['backends']:
                # Set up default backend configuration
                if backend_name == 'openai':
                    config_data['backends'][backend_name] = {
                        'type': 'openai',
                        'default_model': 'gpt-4'
                    }
                elif backend_name == 'groq':
                    config_data['backends'][backend_name] = {
                        'type': 'groq',
                        'default_model': 'mixtral-8x7b-32768'
                    }
                elif backend_name == 'azure_openai':
                    config_data['backends'][backend_name] = {
                        'type': 'openai',
                        'default_model': 'gpt-4',
                        'url': 'https://your-tenant.openai.azure.com/openai/deployments/your-deployment',
                        'api_version': '2023-05-15'
                    }
                    
            # Set the API key
            config_data['backends'][backend_name]['api_key'] = api_key
            
            # Set default backend if not already set
            if 'default_backend' not in config_data:
                config_data['default_backend'] = backend_name
                
            # Write back to config file
            with open(config_path, 'w') as f:
                toml.dump(config_data, f)
                
            return True
            
        except Exception as e:
            console.print(f"Error saving configuration: {e}", style="red")
            return False
            
    async def update_deprecated_models(self) -> None:
        """Update deprecated models to their recommended replacements."""
        if not self.config:
            return
            
        # Known deprecated models and their replacements
        deprecated_models = {
            'mixtral-8x7b-32768': 'llama-3.3-70b-versatile',  # Groq deprecation
            'llama-3.1-70b-versatile': 'llama-3.3-70b-versatile',
            'llama-3.1-70b-specdec': 'llama-3.3-70b-specdec',
            'gemma-7b-it': 'gemma2-9b-it',
        }
        
        updated_any = False
        for backend_name, backend_config in self.config.backends.items():
            if backend_config.default_model in deprecated_models:
                old_model = backend_config.default_model
                new_model = deprecated_models[old_model]
                
                console.print(f"\n⚠️ Updating deprecated model for {backend_name}:")
                console.print(f"  Old: {old_model}")
                console.print(f"  New: {new_model}")
                
                # Update the model in config
                if await self.update_backend_model_in_config(backend_name, new_model):
                    console.print(f"✅ Updated {backend_name} to use {new_model}", style="green")
                    updated_any = True
                else:
                    console.print(f"❌ Failed to update {backend_name}", style="red")
                    
        if updated_any:
            # Reload configuration
            self.config = load_config()
            console.print("\n🔄 Configuration reloaded with updated models")
            
    async def update_backend_model_in_config(self, backend_name: str, new_model: str) -> bool:
        """Update the default model for a backend in the configuration file."""
        try:
            from ..config.loader import get_default_config_path
            import toml
            
            config_path = get_default_config_path()
            
            # Read existing config
            if not config_path.exists():
                return False
                
            with open(config_path, 'r') as f:
                config_data = toml.load(f)
                
            # Update default model
            if 'backends' in config_data and backend_name in config_data['backends']:
                config_data['backends'][backend_name]['default_model'] = new_model
                
                # Write back to config file
                with open(config_path, 'w') as f:
                    toml.dump(config_data, f)
                    
                return True
            
            return False
            
        except Exception as e:
            console.print(f"Error updating model configuration: {e}", style="red")
            return False
            
    async def manage_generation_settings(self) -> None:
        """Manage code generation and validation settings."""
        console.print(Panel(
            Text.assemble(
                ("⚙️ Generation Settings Management\n\n", "bold #0088FF"),
                ("Configure how SnapInfra generates and validates code", "white")
            ),
            title="Settings",
            border_style="#0088FF",
            box=SQUARE
        ))
        
        try:
            from ..config.loader import load_config, get_default_config_path
            config = load_config()
            
            # Display current settings
            settings_table = Table(title="Current Settings", show_header=True, header_style="bold blue")
            settings_table.add_column("Setting", style="cyan", width=30)
            settings_table.add_column("Value", style="white", width=15)
            settings_table.add_column("Description", style="dim white", width=50)
            
            settings_table.add_row(
                "Pure AI Generation", 
                "✅ Enabled" if config.pure_ai_generation else "❌ Disabled",
                "Generate projects using only AI (no fallback templates)"
            )
            settings_table.add_row(
                "Code Validation", 
                "✅ Enabled" if config.validation_enabled else "❌ Disabled",
                "Validate generated code for syntax and consistency"
            )
            settings_table.add_row(
                "Auto-Fix Issues", 
                "✅ Enabled" if config.auto_fix_enabled else "❌ Disabled",
                "Automatically fix common code issues during validation"
            )
            
            console.print(settings_table)
            console.print()
            
            # Setting management menu
            while True:
                action = Prompt.ask(
                    "What would you like to do?",
                    choices=[
                        "toggle-ai", "toggle-validation", "toggle-autofix", 
                        "reset-defaults", "view-config", "done"
                    ],
                    default="done"
                )
                
                if action == "done":
                    break
                elif action == "toggle-ai":
                    await self._toggle_setting("pure_ai_generation", 
                                              not config.pure_ai_generation,
                                              "Pure AI Generation")
                elif action == "toggle-validation":
                    await self._toggle_setting("validation_enabled", 
                                              not config.validation_enabled,
                                              "Code Validation")
                elif action == "toggle-autofix":
                    await self._toggle_setting("auto_fix_enabled", 
                                              not config.auto_fix_enabled,
                                              "Auto-Fix Issues")
                elif action == "reset-defaults":
                    if Confirm.ask("Reset all settings to defaults?", default=False):
                        await self._reset_to_defaults()
                        console.print("✅ Settings reset to defaults", style="green")
                elif action == "view-config":
                    config_path = get_default_config_path()
                    console.print(f"📄 Configuration file: {config_path}")
                    console.print("You can manually edit this file if needed.")
                
                # Reload config to show updated values
                config = load_config()
                
        except Exception as e:
            console.print(f"❌ Error managing settings: {e}", style="red")
    
    async def _toggle_setting(self, setting_name: str, new_value: bool, display_name: str) -> None:
        """Toggle a boolean setting in the configuration."""
        try:
            from ..config.loader import get_default_config_path
            import json
            
            config_path = get_default_config_path()
            
            # Load current config
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update the setting
            config_data[setting_name] = new_value
            
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            status = "enabled" if new_value else "disabled"
            console.print(f"✅ {display_name} {status}", style="green")
            
        except Exception as e:
            console.print(f"❌ Error updating {display_name}: {e}", style="red")
    
    async def _reset_to_defaults(self) -> None:
        """Reset all settings to their default values."""
        try:
            from ..config.loader import get_default_config_path
            import json
            
            config_path = get_default_config_path()
            
            # Load current config
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Reset to defaults
            config_data['pure_ai_generation'] = True
            config_data['validation_enabled'] = True
            config_data['auto_fix_enabled'] = True
            
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            console.print(f"❌ Error resetting settings: {e}", style="red")
            raise
    
    async def manage_api_keys(self) -> None:
        """Interactive API key management interface."""
        while True:
            console.print()
            console.print(Panel(
                Text.assemble(
                    ("🔑 API Key Management\n\n", "bold #0088FF"),
                    ("Manage your AI provider API keys", "white")
                ),
                title="Key Management",
                border_style="#0088FF",
                box=SQUARE
            ))
            console.print()
            
            # Display current API key status
            await self.display_api_key_status()
            
            # Show management options
            console.print("🛠️ Available Actions:")
            actions = [
                ("1", "View API key status"),
                ("2", "Add/Update API key"),
                ("3", "Delete API key"),
                ("4", "Test API key connection"),
                ("q", "Return to chat")
            ]
            
            for action, description in actions:
                console.print(f"  {action}. {description}")
            console.print()
            
            choice = Prompt.ask(
                "Select action",
                choices=["1", "2", "3", "4", "q"],
                default="q"
            )
            
            if choice == "q":
                break
            elif choice == "1":
                continue  # Status is already displayed above
            elif choice == "2":
                await self.add_or_update_api_key()
            elif choice == "3":
                await self.delete_api_key()
            elif choice == "4":
                await self.test_api_key_connection()
                
    async def display_api_key_status(self) -> None:
        """Display current API key status for all backends."""
        if not self.config:
            console.print("No configuration loaded", style="red")
            return
            
        status_table = Table(title="API Key Status", box=ROUNDED, show_header=True, header_style="bold #0088FF")
        status_table.add_column("Provider", style="#0088FF", no_wrap=True)
        status_table.add_column("Status", no_wrap=True)
        status_table.add_column("Key Preview", style="dim")
        status_table.add_column("Default Model", style="white")
        
        for backend_name, backend_config in self.config.backends.items():
            # Check if API key is valid
            api_key = backend_config.api_key
            if (api_key and 
                api_key.strip() and 
                not api_key.startswith('$') and  # Reject unresolved env vars
                api_key not in ['your-api-key', 'None']):
                status = "✅ Configured"
                status_style = "green"
                # Show first 6 and last 4 characters of API key
                if len(api_key) > 10:
                    key_preview = f"{api_key[:6]}...{api_key[-4:]}"
                else:
                    key_preview = f"{api_key[:3]}...{api_key[-2:]}"
            elif api_key and api_key.startswith('$'):
                status = "⚠️ Env Var (not set)"
                status_style = "yellow"
                key_preview = api_key
            else:
                status = "❌ Not configured"
                status_style = "red"
                key_preview = "(none)"
                
            model = backend_config.default_model or "(none)"
            
            status_table.add_row(
                backend_name.title(),
                Text(status, style=status_style),
                key_preview,
                model
            )
            
        console.print(status_table)
        console.print()
        
    async def add_or_update_api_key(self) -> None:
        """Add or update an API key for a backend."""
        console.print("\n🔧 Add/Update API Key")
        
        # Show available backends
        backend_options = [
            ("openai", "OpenAI (GPT-4, GPT-3.5-turbo, etc.)"),
            ("groq", "Groq (Fast inference, Mixtral, Llama)"),
            ("azure_openai", "Azure OpenAI (Enterprise OpenAI)"),
            ("aws_bedrock", "AWS Bedrock (Claude, Titan, etc.)"),
            ("local_ollama", "Local Ollama (Self-hosted models)")
        ]
        
        console.print("\nAvailable Providers:")
        for i, (backend_name, description) in enumerate(backend_options, 1):
            # Show current status
            current_status = ""
            if self.config and backend_name in self.config.backends:
                backend_config = self.config.backends[backend_name]
                if (backend_config.api_key and 
                    backend_config.api_key.strip() and 
                    not backend_config.api_key.startswith('$') and 
                    backend_config.api_key not in ['your-api-key', 'None']):
                    current_status = " [Currently configured]"
                    
            console.print(f"  {i}. {description}{current_status}")
            
        console.print()
        
        try:
            choice = Prompt.ask(
                "Select provider to configure (1-5) or 'cancel'",
                default="cancel"
            )
            
            if choice.lower() == 'cancel':
                return
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(backend_options):
                backend_name, description = backend_options[choice_idx]
                
                console.print(f"\n🔧 Configuring {description}")
                
                # Show current key if exists
                if self.config and backend_name in self.config.backends:
                    current_key = self.config.backends[backend_name].api_key
                    if current_key and current_key.strip():
                        if len(current_key) > 10 and not current_key.startswith('$'):
                            preview = f"{current_key[:6]}...{current_key[-4:]}"
                        else:
                            preview = current_key
                        console.print(f"Current key: {preview}", style="dim")
                        
                        if Confirm.ask("\nReplace existing API key?", default=False):
                            api_key = Prompt.ask(
                                f"Enter new {backend_name.upper()} API key",
                                password=True
                            )
                        else:
                            return
                    else:
                        api_key = Prompt.ask(
                            f"Enter your {backend_name.upper()} API key",
                            password=True
                        )
                else:
                    api_key = Prompt.ask(
                        f"Enter your {backend_name.upper()} API key",
                        password=True
                    )
                
                if api_key and api_key.strip():
                    if await self.save_api_key_to_config(backend_name, api_key.strip()):
                        console.print(f"\n✅ {backend_name.upper()} API key saved successfully!", style="green")
                        
                        # Reload config
                        self.config = load_config()
                        
                        # Ask if user wants to test the connection
                        if Confirm.ask("Test the API key connection?", default=True):
                            await self.test_specific_api_key(backend_name)
                    else:
                        console.print(f"\n❌ Failed to save {backend_name.upper()} API key", style="red")
                else:
                    console.print("\n⚠️ Empty API key, operation cancelled", style="yellow")
            else:
                console.print("Invalid choice", style="red")
                
        except ValueError:
            console.print("Invalid choice", style="red")
            
    async def delete_api_key(self) -> None:
        """Delete an API key for a backend."""
        console.print("\n🗑️ Delete API Key")
        
        if not self.config:
            console.print("No configuration loaded", style="red")
            return
            
        # Find backends with API keys
        configured_backends = []
        for backend_name, backend_config in self.config.backends.items():
            if (backend_config.api_key and 
                backend_config.api_key.strip() and 
                backend_config.api_key not in ['your-api-key', 'None']):
                configured_backends.append((backend_name, backend_config))
                
        if not configured_backends:
            console.print("\n⚠️ No API keys are currently configured", style="yellow")
            return
            
        console.print("\nConfigured Providers:")
        for i, (backend_name, backend_config) in enumerate(configured_backends, 1):
            key_preview = ""
            if backend_config.api_key and not backend_config.api_key.startswith('$'):
                if len(backend_config.api_key) > 10:
                    key_preview = f" ({backend_config.api_key[:6]}...{backend_config.api_key[-4:]})"
                else:
                    key_preview = f" ({backend_config.api_key[:3]}...{backend_config.api_key[-2:]})"
                    
            console.print(f"  {i}. {backend_name.title()}{key_preview}")
            
        console.print()
        
        try:
            choice = Prompt.ask(
                f"Select provider to delete API key (1-{len(configured_backends)}) or 'cancel'",
                default="cancel"
            )
            
            if choice.lower() == 'cancel':
                return
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(configured_backends):
                backend_name, backend_config = configured_backends[choice_idx]
                
                # Confirm deletion
                if Confirm.ask(f"\n⚠️ Delete API key for {backend_name.title()}?", default=False):
                    if await self.remove_api_key_from_config(backend_name):
                        console.print(f"\n✅ {backend_name.upper()} API key deleted successfully!", style="green")
                        
                        # Reload config
                        self.config = load_config()
                        
                        # If this was the current backend, user needs to select a new one
                        if backend_name == self.current_backend_name:
                            console.print(f"\n⚠️ You were using {backend_name.upper()} backend. Please select a new backend.", style="yellow")
                            self.current_backend_name = None
                            self.backend = None
                    else:
                        console.print(f"\n❌ Failed to delete {backend_name.upper()} API key", style="red")
                else:
                    console.print("\n🚫 Deletion cancelled", style="dim")
            else:
                console.print("Invalid choice", style="red")
                
        except ValueError:
            console.print("Invalid choice", style="red")
            
    async def remove_api_key_from_config(self, backend_name: str) -> bool:
        """Remove an API key from the configuration file."""
        try:
            from ..config.loader import get_default_config_path
            import toml
            
            config_path = get_default_config_path()
            
            # Read existing config
            if not config_path.exists():
                console.print("Configuration file not found", style="red")
                return False
                
            with open(config_path, 'r') as f:
                config_data = toml.load(f)
                
            # Remove API key
            if 'backends' in config_data and backend_name in config_data['backends']:
                if 'api_key' in config_data['backends'][backend_name]:
                    del config_data['backends'][backend_name]['api_key']
                    
                    # If this backend has no other config, we might want to keep the structure
                    # but remove the api_key. For minimal configs, we could remove the whole backend.
                    # Let's keep the backend structure but without api_key
                    
                    # Write back to config file
                    with open(config_path, 'w') as f:
                        toml.dump(config_data, f)
                        
                    return True
            
            return False
            
        except Exception as e:
            console.print(f"Error removing API key: {e}", style="red")
            return False
            
    async def test_api_key_connection(self) -> None:
        """Test API key connections for configured backends."""
        console.print("\n🧪 Test API Key Connections")
        
        if not self.config:
            console.print("No configuration loaded", style="red")
            return
            
        # Find backends with API keys
        configured_backends = []
        for backend_name, backend_config in self.config.backends.items():
            if (backend_config.api_key and 
                backend_config.api_key.strip() and 
                not backend_config.api_key.startswith('$') and
                backend_config.api_key not in ['your-api-key', 'None']):
                configured_backends.append((backend_name, backend_config))
                
        if not configured_backends:
            console.print("\n⚠️ No API keys are currently configured", style="yellow")
            return
            
        console.print("\nTesting configured providers...\n")
        
        for backend_name, backend_config in configured_backends:
            await self.test_specific_api_key(backend_name, backend_config)
            
    async def test_specific_api_key(self, backend_name: str, backend_config = None) -> None:
        """Test a specific API key connection."""
        if not backend_config and self.config:
            backend_config = self.config.backends.get(backend_name)
            
        if not backend_config:
            console.print(f"❌ {backend_name.title()}: Configuration not found", style="red")
            return
            
        console.print(f"🧪 Testing {backend_name.title()}...", end=" ")
        
        try:
            # Create a temporary backend instance
            test_backend = create_backend(backend_config)
            
            # Test by listing models (quick API call)
            with Progress(SpinnerColumn(), TextColumn(""), console=console, disable=True):
                models = await test_backend.list_models()
            
            if models:
                console.print(f"✅ Connected! Found {len(models)} models", style="green")
            else:
                console.print("⚠️ Connected but no models found", style="yellow")
                
        except Exception as e:
            console.print(f"❌ Failed: {str(e)[:50]}...", style="red")
            
    async def generate_comprehensive_project(self) -> None:
        """Generate a complete project with multiple files, proper structure, and Docker support."""
        console.print(Panel(
            Text.assemble(
                ("🚀 Comprehensive Project Generator\n\n", "bold #0088FF"),
                ("Generate complete, production-ready projects with:\n", "white"),
                ("• Multiple files and proper folder structure\n", "white"),
                ("• Docker configuration and containerization\n", "white"),
                ("• Documentation and setup instructions\n", "white"),
                ("• Save to current directory, desktop, or custom path\n", "white"),
                ("• Automatic project directory creation", "white")
            ),
            title="Project Generator",
            border_style="#0088FF",
            box=SQUARE
        ))
        console.print()
        
        # Get project description from user
        project_description = Prompt.ask(
            "Describe the project you want to generate",
            default="todo app with REST API and frontend"
        )
        
        # Get project name
        default_name = self._extract_project_name(project_description)
        project_name = Prompt.ask(
            "Project name",
            default=default_name
        )
        
        # Validate project name
        project_name = self._sanitize_project_name(project_name)
        
        # Get output directory
        output_dir = Prompt.ask(
            "Output directory",
            default=f"./generated_projects/{project_name}"
        )
        
        console.print(f"\n🔍 Analyzing project: {project_description}")
        
        # Detect project type and create generation plan
        project_plan = await self._create_project_plan(project_description, project_name)
        
        if not project_plan:
            console.print("❌ Failed to create project plan", style="red")
            return
            
        # Display project plan
        await self._display_project_plan(project_plan)
        
        # Confirm generation
        if not Confirm.ask("\nProceed with project generation?", default=True):
            console.print("🚫 Project generation cancelled", style="yellow")
            return
            
        # Generate the complete project
        success = await self._execute_project_generation(project_plan, output_dir)
        
        if success:
            console.print(f"\n🎉 Project generated successfully at: {output_dir}", style="bold green")
            console.print(f"📁 Project structure created with {len(project_plan['files'])} files")
            
            # Show next steps
            await self._display_next_steps(output_dir, project_plan)
        else:
            console.print("❌ Project generation failed", style="red")
            
    def _extract_project_name(self, description: str) -> str:
        """Extract a reasonable project name from description."""
        # Simple extraction logic - take first few meaningful words
        words = description.lower().replace("-", " ").replace("_", " ").split()
        meaningful_words = [w for w in words if w not in ['a', 'an', 'the', 'with', 'for', 'and', 'or', 'but']]
        return "-".join(meaningful_words[:3]) if meaningful_words else "generated-project"
        
    def _sanitize_project_name(self, name: str) -> str:
        """Sanitize project name for filesystem compatibility."""
        import re
        # Replace spaces and special chars with hyphens, lowercase
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '-', name.lower())
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip('-')
        
    # Removed _is_project_description method - we always generate comprehensive projects now
        
    async def _create_project_plan(self, description: str, project_name: str) -> dict:
        """Create a comprehensive project generation plan."""
        # Check if pure AI generation is enabled (default=True)
        from ..config.loader import load_config
        try:
            config = load_config()
            pure_ai_mode = config.pure_ai_generation
        except Exception:
            pure_ai_mode = True  # Default to pure AI mode if config fails
            
        if pure_ai_mode:
            console.print("🤖 Pure AI generation mode enabled - no fallback templates will be used", style="dim blue")
            
        if not self.backend:
            console.print("❌ No AI backend available", style="red")
            return None
            
        # Use AI to analyze project requirements and create plan
        planning_prompt = f"""
        Analyze this project description and create a comprehensive development plan:
        
        Project: {description}
        Name: {project_name}
        
        Create a JSON response with the following structure:
        {{
            "project_type": "web_app",  // web_app, api, cli, mobile, etc.
            "tech_stack": ["nodejs", "react", "docker"],  // main technologies
            "description": "Brief project description",
            "files": [
                {{
                    "path": "src/app.js",
                    "type": "backend",
                    "description": "Main application server",
                    "priority": 1
                }},
                {{
                    "path": "frontend/src/App.jsx",
                    "type": "frontend",
                    "description": "Main React component",
                    "priority": 2
                }}
            ],
            "folders": ["src", "frontend/src", "docker", "docs"],
            "docker_needed": true,
            "database": "sqlite",  // or null if not needed
            "api_endpoints": 5,  // estimated number
            "complexity": "medium"  // low, medium, high
        }}
        
        Focus on creating a production-ready project structure with proper separation of concerns.
        """
        
        try:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Creating project plan...", total=None)
                
                conversation = self.backend.chat(self.current_model)
                response = await conversation.send(planning_prompt)
                
            # Parse JSON response
            import json
            import re
            
            # PURE AI MODE - Extract JSON with comprehensive parsing strategies
            raw_response = response.full_output.strip()
            console.print(f"🔍 Raw AI response ({len(raw_response)} chars): {raw_response[:200]}...", style="dim")
            
            # Clean the response first
            cleaned_response = self._clean_ai_response(raw_response)
            
            # Multiple aggressive JSON extraction patterns
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',  # JSON in code blocks
                r'```\s*([\s\S]*?)\s*```',     # Any code block
                r'({[\s\S]*"files"[\s\S]*})',  # Object containing "files" key
                r'({[\s\S]*"project_type"[\s\S]*})',  # Object containing "project_type"
                r'(\{[\s\S]*\})',              # Most permissive - any JSON object
            ]
            
            for i, pattern in enumerate(json_patterns, 1):
                console.print(f"🔍 Trying extraction pattern {i}...", style="dim")
                matches = re.finditer(pattern, cleaned_response, re.DOTALL)
                
                for match in matches:
                    json_candidate = match.group(1) if match.groups() else match.group(0)
                    json_candidate = json_candidate.strip()
                    
                    if len(json_candidate) < 20:  # Skip tiny matches
                        continue
                    
                    console.print(f"📝 JSON candidate ({len(json_candidate)} chars): {json_candidate[:150]}...", style="dim cyan")
                    
                    # Try to fix common JSON issues
                    fixed_json = self._fix_json_issues(json_candidate)
                    
                    try:
                        parsed_plan = json.loads(fixed_json)
                        
                        # Validate it's a meaningful project plan
                        if self._validate_ai_project_plan(parsed_plan):
                            file_count = len(parsed_plan.get('files', []))
                            tech_stack = ', '.join(parsed_plan.get('tech_stack', []))
                            console.print(f"✅ Successfully parsed AI project plan!", style="bold green")
                            console.print(f"   📁 Files: {file_count}")
                            console.print(f"   🛠️  Tech: {tech_stack}")
                            console.print(f"   📋 Type: {parsed_plan.get('project_type', 'unknown')}")
                            return parsed_plan
                        else:
                            console.print(f"⚠️ JSON parsed but doesn't look like a project plan", style="dim yellow")
                            
                    except json.JSONDecodeError as e:
                        console.print(f"💥 JSON parse error: {str(e)[:100]}", style="dim red")
                        continue
            
            # If we get here, all parsing failed - retry with better prompt
            console.print("🔄 JSON parsing failed, retrying with enhanced prompt...", style="yellow")
            return await self._retry_ai_planning(description, project_name)
            
        except Exception as e:
            console.print(f"Error creating project plan: {e}", style="red")
            return await self._retry_ai_planning(description, project_name)
            
    async def _retry_ai_planning(self, description: str, project_name: str) -> dict:
        """Retry AI planning with a more detailed and specific prompt."""
        if not self.backend:
            console.print("❌ No AI backend available for retry", style="red")
            return None
            
        # Enhanced retry prompt with more specific instructions
        retry_prompt = f"""
        You are an expert software architect. Create a COMPLETE project plan for:
        
        PROJECT DESCRIPTION: {description}
        PROJECT NAME: {project_name}
        
        CRITICAL: You MUST respond with a valid JSON object that includes:
        
        {{
            "project_type": "[web_app|api|cli|mobile|desktop|microservice|etc]",
            "tech_stack": ["list", "of", "technologies"],
            "description": "Brief but comprehensive project description",
            "files": [
                {{
                    "path": "exact/file/path.ext",
                    "type": "[backend|frontend|config|docs|docker|iac|cicd|script|test|api]",
                    "description": "What this file does",
                    "priority": 1
                }}
            ],
            "folders": ["list", "of", "required", "directories"],
            "docker_needed": true,
            "database": "database_type_or_null",
            "api_endpoints": 5,
            "complexity": "[low|medium|high]"
        }}
        
        REQUIREMENTS FOR FILES ARRAY:
        - Include ALL necessary files for a complete, production-ready project
        - Minimum 8 files for simple projects, 15+ for web apps, 20+ for complex projects
        - Include: source code, configuration, documentation, deployment, testing
        - Each file must have a realistic path and clear purpose
        - Prioritize files 1-8 based on importance
        
        PROJECT ANALYSIS:
        Based on '{description}', determine what type of project this is and what files it needs:
        - If it's a web app: frontend, backend, database, deployment configs, docs
        - If it's an API: server code, routes, models, tests, deployment, docs
        - If it's a CLI tool: main script, config, docs, tests, packaging
        - If it's mobile: app code, screens, services, build configs, docs
        
        Generate a complete, realistic project structure that a real developer would create.
        Respond with ONLY the JSON object, no other text.
        """
        
        try:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Retrying AI project planning...", total=None)
                
                conversation = self.backend.chat(self.current_model)
                response = await conversation.send(retry_prompt)
                
            # Parse JSON response with more aggressive extraction
            import json
            import re
            
            # Try multiple JSON extraction strategies
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',      # JSON in code blocks
                r'```\s*([\s\S]*?)\s*```',          # Any code block
                r'\{[\s\S]*"files"[\s\S]*\}',        # Object with files property
                r'\{[\s\S]*\}',                      # Any JSON object
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, response.full_output, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1) if json_match.groups() else json_match.group(0)
                    try:
                        plan = json.loads(json_text.strip())
                        
                        # Validate that this is a valid project plan
                        if (isinstance(plan, dict) and 
                            'files' in plan and 
                            isinstance(plan['files'], list) and
                            len(plan['files']) >= 3):  # Minimum viable project
                            
                            file_count = len(plan.get('files', []))
                            console.print(f"✅ AI generated project plan with {file_count} files")
                            return plan
                            
                    except json.JSONDecodeError as e:
                        console.print(f"JSON parsing error: {e}", style="dim red")
                        continue
            
            # NO FALLBACKS - Keep retrying until we get pure AI generated content
            console.print("❌ Failed to parse AI response after all attempts", style="red")
            console.print("🔄 Trying one more time with maximum clarity prompt...", style="yellow")
            return await self._final_ai_attempt(description, project_name)
            
        except Exception as e:
            console.print(f"Error in AI planning retry: {e}", style="red")
            return await self._create_minimal_ai_project(description, project_name)
    
    async def _create_minimal_ai_project(self, description: str, project_name: str) -> dict:
        """Create a minimal project structure using AI guidance when JSON parsing fails."""
        
        # Use AI to determine basic project characteristics without requiring JSON
        analysis_prompt = f"""
        Analyze this project: "{description}"
        
        Answer these questions in a simple format:
        1. What type of project is this? (web app, api, cli tool, mobile app, etc.)
        2. What are the main technologies needed? (list 3-5 key technologies)
        3. How many files would a typical project like this have? (number between 5-30)
        4. Does it need Docker? (yes/no)
        5. Does it need a database? (specify type or 'none')
        
        Keep your answers brief and direct.
        """
        
        try:
            conversation = self.backend.chat(self.current_model)
            analysis = await conversation.send(analysis_prompt)
            
            # Extract basic info from analysis
            analysis_text = analysis.full_output.lower()
            
            # Determine project type
            if any(word in analysis_text for word in ['web app', 'website', 'frontend']):
                project_type = 'web_app'
                base_files = ['src/index.html', 'src/app.js', 'src/styles.css', 'package.json', 'README.md']
            elif any(word in analysis_text for word in ['api', 'rest', 'server', 'backend']):
                project_type = 'api'
                base_files = ['src/server.js', 'src/routes/api.js', 'package.json', 'README.md']
            elif any(word in analysis_text for word in ['cli', 'command', 'terminal']):
                project_type = 'cli'
                base_files = ['src/cli.js', 'package.json', 'README.md']
            else:
                project_type = 'application'
                base_files = ['src/main.js', 'package.json', 'README.md']
            
            # Extract file count from analysis
            file_count_match = re.search(r'(\d+)', analysis_text)
            target_files = int(file_count_match.group(1)) if file_count_match else 8
            target_files = max(5, min(target_files, 25))  # Keep reasonable bounds
            
            # Generate additional files using AI to reach target count
            if len(base_files) < target_files:
                additional_files = await self._generate_additional_files(description, project_name, base_files, target_files - len(base_files))
                base_files.extend(additional_files)
            
            # Create project plan structure
            return {
                "project_type": project_type,
                "tech_stack": self._extract_technologies(analysis_text),
                "description": f"AI-generated project: {description}",
                "files": [
                    {
                        "path": file_path,
                        "type": self._determine_file_type(file_path),
                        "description": f"Generated file for {project_name}",
                        "priority": idx + 1
                    }
                    for idx, file_path in enumerate(base_files)
                ],
                "folders": list(set([str(Path(f).parent) for f in base_files if str(Path(f).parent) != '.'])),
                "docker_needed": 'yes' in analysis_text and 'docker' in analysis_text,
                "database": self._extract_database_type(analysis_text),
                "api_endpoints": 3 if 'api' in analysis_text else 0,
                "complexity": "medium"
            }
            
        except Exception as e:
            console.print(f"Error creating minimal project: {e}", style="red")
            return None
    
    async def _generate_additional_files(self, description: str, project_name: str, existing_files: list, count_needed: int) -> list:
        """Generate additional files using AI to complete the project structure."""
        additional_prompt = f"""
        For the project "{description}" (name: {project_name}), I already have these files:
        {', '.join(existing_files)}
        
        I need {count_needed} more files to complete this project. 
        What additional files would be essential? List them as simple file paths, one per line.
        
        Examples of types of files that might be needed:
        - Configuration files (config.json, .env.example)
        - Additional source files (utils.js, helpers.js, components/)
        - Test files (tests/, *.test.js)
        - Documentation (docs/, CONTRIBUTING.md)
        - Build/deployment files (Dockerfile, .github/workflows/)
        
        Respond with exactly {count_needed} file paths, one per line, no explanations.
        """
        
        try:
            conversation = self.backend.chat(self.current_model)
            response = await conversation.send(additional_prompt)
            
            # Extract file paths from response
            lines = response.full_output.strip().split('\n')
            additional_files = []
            
            for line in lines:
                # Clean up the line and extract file path
                clean_line = re.sub(r'^[-*\d\.\s]+', '', line.strip())
                if clean_line and '/' in clean_line or '.' in clean_line:
                    additional_files.append(clean_line)
                    
            return additional_files[:count_needed]
            
        except Exception as e:
            console.print(f"Error generating additional files: {e}", style="yellow")
            return []
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type based on path and extension."""
        path_lower = file_path.lower()
        
        if any(ext in path_lower for ext in ['.js', '.ts', '.py']) and 'test' not in path_lower:
            if any(word in path_lower for word in ['server', 'api', 'backend', 'app']):
                return 'backend'
            elif any(word in path_lower for word in ['component', 'frontend', 'client']):
                return 'frontend'
            else:
                return 'backend'
        elif any(ext in path_lower for ext in ['package.json', '.env', 'config', '.yaml', '.yml']):
            return 'config'
        elif any(ext in path_lower for ext in ['docker', 'compose']):
            return 'docker'
        elif 'test' in path_lower:
            return 'test'
        elif any(ext in path_lower for ext in ['.md', 'readme', 'doc']):
            return 'docs'
        else:
            return 'backend'
    
    def _extract_technologies(self, analysis_text: str) -> list:
        """Extract technology stack from AI analysis."""
        # Common technologies to look for
        techs = []
        tech_patterns = {
            'react': r'\breact\b',
            'node': r'\bnode\b|\bnodejs\b',
            'express': r'\bexpress\b',
            'python': r'\bpython\b',
            'flask': r'\bflask\b',
            'django': r'\bdjango\b',
            'javascript': r'\bjavascript\b|\bjs\b',
            'typescript': r'\btypescript\b|\bts\b',
            'html': r'\bhtml\b',
            'css': r'\bcss\b',
            'docker': r'\bdocker\b',
            'mongodb': r'\bmongo\b|\bmongodb\b',
            'postgresql': r'\bpostgres\b|\bpostgresql\b',
            'mysql': r'\bmysql\b',
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, analysis_text):
                techs.append(tech)
        
        return techs if techs else ['javascript', 'node']
    
    def _extract_database_type(self, analysis_text: str) -> str:
        """Extract database type from analysis."""
        if 'mongodb' in analysis_text or 'mongo' in analysis_text:
            return 'mongodb'
        elif 'postgresql' in analysis_text or 'postgres' in analysis_text:
            return 'postgresql'
        elif 'mysql' in analysis_text:
            return 'mysql'
        elif 'sqlite' in analysis_text:
            return 'sqlite'
        elif 'none' in analysis_text or 'no database' in analysis_text:
            return None
        else:
            return 'sqlite'  # Safe default
    
    def _get_fallback_project_template(self, project_type: str, description: str) -> dict:
        """Get fallback project template when AI parsing fails completely."""
        if project_type == 'web_app':
            return {
                "project_type": "web_app",
                "tech_stack": ["nodejs", "express", "react", "docker", "terraform", "kubernetes"],
                "description": f"Full-stack web application: {description}",
                "files": [
                    # Backend API files
                    {"path": "backend/server.js", "type": "backend", "description": "Express server with middleware setup", "priority": 1},
                    {"path": "backend/package.json", "type": "config", "description": "Backend dependencies", "priority": 1},
                    {"path": "backend/routes/api.js", "type": "backend", "description": "Main API routes", "priority": 1},
                    {"path": "backend/routes/auth.js", "type": "backend", "description": "Authentication routes", "priority": 1},
                    {"path": "backend/routes/users.js", "type": "backend", "description": "User management routes", "priority": 1},
                    {"path": "backend/controllers/authController.js", "type": "backend", "description": "Authentication controller", "priority": 1},
                    {"path": "backend/controllers/userController.js", "type": "backend", "description": "User management controller", "priority": 1},
                    {"path": "backend/models/User.js", "type": "backend", "description": "User database model", "priority": 1},
                    {"path": "backend/models/index.js", "type": "backend", "description": "Database models index", "priority": 1},
                    {"path": "backend/middleware/auth.js", "type": "backend", "description": "Authentication middleware", "priority": 1},
                    {"path": "backend/middleware/validation.js", "type": "backend", "description": "Input validation middleware", "priority": 1},
                    {"path": "backend/middleware/errorHandler.js", "type": "backend", "description": "Error handling middleware", "priority": 1},
                    {"path": "backend/config/database.js", "type": "backend", "description": "Database configuration", "priority": 1},
                    {"path": "backend/config/passport.js", "type": "backend", "description": "Passport.js authentication config", "priority": 1},
                    {"path": "backend/utils/jwt.js", "type": "backend", "description": "JWT token utilities", "priority": 1},
                    {"path": "backend/utils/logger.js", "type": "backend", "description": "Logging utilities", "priority": 1},
                    {"path": "backend/migrations/001_create_users_table.js", "type": "backend", "description": "Users table migration", "priority": 1},
                    {"path": "backend/seeders/default_users.js", "type": "backend", "description": "Default user data seeder", "priority": 1},
                    # Frontend files
                    {"path": "frontend/src/App.jsx", "type": "frontend", "description": "React main component", "priority": 2},
                    {"path": "frontend/package.json", "type": "config", "description": "Frontend dependencies", "priority": 2},
                    {"path": "frontend/src/services/api.js", "type": "frontend", "description": "API service layer", "priority": 2},
                    {"path": "frontend/src/components/Auth/Login.jsx", "type": "frontend", "description": "Login component", "priority": 2},
                    {"path": "frontend/src/components/Auth/Register.jsx", "type": "frontend", "description": "Registration component", "priority": 2},
                    {"path": "frontend/src/hooks/useAuth.js", "type": "frontend", "description": "Authentication hook", "priority": 2},
                    {"path": "frontend/src/context/AuthContext.js", "type": "frontend", "description": "Authentication context", "priority": 2},
                    # Infrastructure as Code - Multi-Cloud
                    {"path": "infrastructure/terraform/aws/main.tf", "type": "iac", "description": "AWS Terraform infrastructure", "priority": 3},
                    {"path": "infrastructure/terraform/aws/variables.tf", "type": "iac", "description": "AWS Terraform variables", "priority": 3},
                    {"path": "infrastructure/terraform/aws/outputs.tf", "type": "iac", "description": "AWS Terraform outputs", "priority": 3},
                    {"path": "infrastructure/terraform/gcp/main.tf", "type": "iac", "description": "Google Cloud Terraform infrastructure", "priority": 3},
                    {"path": "infrastructure/terraform/gcp/variables.tf", "type": "iac", "description": "Google Cloud Terraform variables", "priority": 3},
                    {"path": "infrastructure/terraform/azure/main.tf", "type": "iac", "description": "Azure Terraform infrastructure", "priority": 3},
                    {"path": "infrastructure/terraform/azure/variables.tf", "type": "iac", "description": "Azure Terraform variables", "priority": 3},
                    {"path": "infrastructure/cloudformation/aws-stack.yaml", "type": "iac", "description": "AWS CloudFormation template", "priority": 3},
                    {"path": "infrastructure/gcp/deployment-manager.yaml", "type": "iac", "description": "Google Cloud Deployment Manager", "priority": 3},
                    {"path": "infrastructure/azure/arm-template.json", "type": "iac", "description": "Azure ARM template", "priority": 3},
                    {"path": "infrastructure/kubernetes/deployment.yaml", "type": "iac", "description": "Kubernetes deployment", "priority": 4},
                    {"path": "infrastructure/kubernetes/service.yaml", "type": "iac", "description": "Kubernetes service", "priority": 4},
                    {"path": "infrastructure/kubernetes/ingress.yaml", "type": "iac", "description": "Kubernetes ingress", "priority": 4},
                    # Docker and deployment - Multi-cloud
                    {"path": "docker-compose.yml", "type": "docker", "description": "Local development orchestration", "priority": 5},
                    {"path": "docker-compose.prod.yml", "type": "docker", "description": "Production Docker orchestration", "priority": 5},
                    {"path": "Dockerfile.backend", "type": "docker", "description": "Backend Docker image", "priority": 5},
                    {"path": "Dockerfile.frontend", "type": "docker", "description": "Frontend Docker image", "priority": 5},
                    {"path": "docker/aws/docker-compose.aws.yml", "type": "docker", "description": "AWS ECS Docker configuration", "priority": 5},
                    {"path": "docker/gcp/docker-compose.gcp.yml", "type": "docker", "description": "Google Cloud Run configuration", "priority": 5},
                    {"path": "docker/azure/docker-compose.azure.yml", "type": "docker", "description": "Azure Container Instances config", "priority": 5},
                    {"path": "docker/nginx/nginx.conf", "type": "docker", "description": "Nginx reverse proxy config", "priority": 5},
                    {"path": "docker/nginx/Dockerfile.nginx", "type": "docker", "description": "Nginx Docker image", "priority": 5},
                    # CI/CD and deployment - Multi-cloud
                    {"path": ".github/workflows/deploy.yml", "type": "cicd", "description": "GitHub Actions multi-cloud deployment", "priority": 6},
                    {"path": ".github/workflows/test.yml", "type": "cicd", "description": "GitHub Actions testing pipeline", "priority": 6},
                    {"path": "scripts/deploy.sh", "type": "script", "description": "Universal deployment script", "priority": 6},
                    {"path": "scripts/deploy-aws.sh", "type": "script", "description": "AWS deployment script", "priority": 6},
                    {"path": "scripts/deploy-gcp.sh", "type": "script", "description": "Google Cloud deployment script", "priority": 6},
                    {"path": "scripts/deploy-azure.sh", "type": "script", "description": "Azure deployment script", "priority": 6},
                    {"path": "scripts/setup.sh", "type": "script", "description": "Environment setup script", "priority": 6},
                    {"path": "scripts/build-images.sh", "type": "script", "description": "Docker image build script", "priority": 6},
                    {"path": "scripts/run-tests.sh", "type": "script", "description": "Test execution script", "priority": 6},
                    # API Testing and Documentation
                    {"path": "backend/tests/auth.test.js", "type": "test", "description": "Authentication tests", "priority": 6},
                    {"path": "backend/tests/api.test.js", "type": "test", "description": "API endpoint tests", "priority": 6},
                    {"path": "backend/tests/models.test.js", "type": "test", "description": "Database model tests", "priority": 6},
                    {"path": "api/openapi.yaml", "type": "api", "description": "OpenAPI 3.0 specification", "priority": 6},
                    {"path": "api/postman_collection.json", "type": "api", "description": "Postman API collection", "priority": 6},
                    {"path": "api/insomnia_workspace.json", "type": "api", "description": "Insomnia REST client workspace", "priority": 6},
                    # Configuration and documentation
                    {"path": ".env.example", "type": "config", "description": "Environment variables template", "priority": 7},
                    {"path": "README.md", "type": "docs", "description": "Project documentation", "priority": 8},
                    {"path": "docs/DEPLOYMENT.md", "type": "docs", "description": "Deployment guide", "priority": 8},
                    {"path": "docs/API.md", "type": "docs", "description": "API documentation", "priority": 8}
                ],
                "folders": ["backend", "backend/routes", "backend/controllers", "backend/models", "backend/middleware", 
                           "backend/config", "backend/utils", "backend/migrations", "backend/seeders", "backend/tests",
                           "frontend/src", "frontend/src/components", "frontend/src/components/Auth", 
                           "frontend/src/services", "frontend/src/hooks", "frontend/src/context", "frontend/public",
                           "infrastructure/terraform/aws", "infrastructure/terraform/gcp", "infrastructure/terraform/azure",
                           "infrastructure/cloudformation", "infrastructure/gcp", "infrastructure/azure", 
                           "infrastructure/kubernetes", 
                           "docker/aws", "docker/gcp", "docker/azure", "docker/nginx",
                           "api", ".github/workflows", "scripts", "docs"],
                "docker_needed": True,
                "database": "sqlite",
                "api_endpoints": 5,
                "complexity": "medium"
            }
        elif project_type == 'api':
            return {
                "project_type": "api",
                "tech_stack": ["nodejs", "express", "docker", "terraform", "kubernetes"],
                "description": f"REST API service: {description}",
                "files": [
                    # Core API application files
                    {"path": "src/server.js", "type": "backend", "description": "Main API server with middleware", "priority": 1},
                    {"path": "package.json", "type": "config", "description": "Dependencies and scripts", "priority": 1},
                    {"path": "src/app.js", "type": "backend", "description": "Express app configuration", "priority": 1},
                    # API Routes and Controllers
                    {"path": "src/routes/index.js", "type": "backend", "description": "Main routes index", "priority": 1},
                    {"path": "src/routes/api.js", "type": "backend", "description": "Core API routes", "priority": 1},
                    {"path": "src/routes/auth.js", "type": "backend", "description": "Authentication routes", "priority": 1},
                    {"path": "src/routes/users.js", "type": "backend", "description": "User management routes", "priority": 1},
                    {"path": "src/routes/health.js", "type": "backend", "description": "Health check routes", "priority": 1},
                    {"path": "src/controllers/authController.js", "type": "backend", "description": "Authentication controller", "priority": 1},
                    {"path": "src/controllers/userController.js", "type": "backend", "description": "User management controller", "priority": 1},
                    {"path": "src/controllers/baseController.js", "type": "backend", "description": "Base controller class", "priority": 1},
                    # Database Models and Config
                    {"path": "src/models/index.js", "type": "backend", "description": "Database models index", "priority": 1},
                    {"path": "src/models/User.js", "type": "backend", "description": "User model", "priority": 1},
                    {"path": "src/models/BaseModel.js", "type": "backend", "description": "Base model class", "priority": 1},
                    {"path": "src/config/database.js", "type": "backend", "description": "Database configuration", "priority": 1},
                    {"path": "src/config/redis.js", "type": "backend", "description": "Redis cache configuration", "priority": 1},
                    {"path": "src/config/passport.js", "type": "backend", "description": "Passport authentication config", "priority": 1},
                    # Middleware
                    {"path": "src/middleware/auth.js", "type": "backend", "description": "Authentication middleware", "priority": 1},
                    {"path": "src/middleware/validation.js", "type": "backend", "description": "Request validation middleware", "priority": 1},
                    {"path": "src/middleware/errorHandler.js", "type": "backend", "description": "Error handling middleware", "priority": 1},
                    {"path": "src/middleware/rateLimiter.js", "type": "backend", "description": "Rate limiting middleware", "priority": 1},
                    {"path": "src/middleware/cors.js", "type": "backend", "description": "CORS configuration middleware", "priority": 1},
                    {"path": "src/middleware/helmet.js", "type": "backend", "description": "Security headers middleware", "priority": 1},
                    # Utilities and Services
                    {"path": "src/utils/jwt.js", "type": "backend", "description": "JWT token utilities", "priority": 1},
                    {"path": "src/utils/logger.js", "type": "backend", "description": "Winston logger configuration", "priority": 1},
                    {"path": "src/utils/validator.js", "type": "backend", "description": "Input validation utilities", "priority": 1},
                    {"path": "src/services/emailService.js", "type": "backend", "description": "Email service integration", "priority": 1},
                    {"path": "src/services/cacheService.js", "type": "backend", "description": "Cache service utilities", "priority": 1},
                    # Database Migrations and Seeds
                    {"path": "src/migrations/20240101000000_create_users_table.js", "type": "backend", "description": "Users table migration", "priority": 1},
                    {"path": "src/migrations/20240101000001_create_sessions_table.js", "type": "backend", "description": "Sessions table migration", "priority": 1},
                    {"path": "src/seeders/defaultUsers.js", "type": "backend", "description": "Default user data seeder", "priority": 1},
                    # Infrastructure as Code - Multi-Cloud
                    {"path": "infrastructure/terraform/aws/main.tf", "type": "iac", "description": "AWS Terraform infrastructure", "priority": 2},
                    {"path": "infrastructure/terraform/aws/variables.tf", "type": "iac", "description": "AWS Terraform variables", "priority": 2},
                    {"path": "infrastructure/terraform/gcp/main.tf", "type": "iac", "description": "Google Cloud Terraform infrastructure", "priority": 2},
                    {"path": "infrastructure/terraform/azure/main.tf", "type": "iac", "description": "Azure Terraform infrastructure", "priority": 2},
                    {"path": "infrastructure/cloudformation/api-stack.yaml", "type": "iac", "description": "AWS CloudFormation API stack", "priority": 2},
                    {"path": "infrastructure/gcp/deployment-manager.yaml", "type": "iac", "description": "Google Cloud Deployment Manager", "priority": 2},
                    {"path": "infrastructure/azure/arm-template.json", "type": "iac", "description": "Azure ARM template for API", "priority": 2},
                    {"path": "infrastructure/kubernetes/deployment.yaml", "type": "iac", "description": "Kubernetes deployment", "priority": 3},
                    {"path": "infrastructure/kubernetes/service.yaml", "type": "iac", "description": "Kubernetes service", "priority": 3},
                    # Docker and deployment - Multi-cloud
                    {"path": "Dockerfile", "type": "docker", "description": "Production API container", "priority": 4},
                    {"path": "Dockerfile.dev", "type": "docker", "description": "Development container", "priority": 4},
                    {"path": "docker-compose.yml", "type": "docker", "description": "Local development orchestration", "priority": 4},
                    {"path": "docker-compose.prod.yml", "type": "docker", "description": "Production orchestration", "priority": 4},
                    {"path": "docker/aws/ecs-task-definition.json", "type": "docker", "description": "AWS ECS task definition", "priority": 4},
                    {"path": "docker/gcp/cloud-run.yaml", "type": "docker", "description": "Google Cloud Run config", "priority": 4},
                    {"path": "docker/azure/container-instance.yaml", "type": "docker", "description": "Azure Container Instance config", "priority": 4},
                    {"path": "docker/nginx/nginx.conf", "type": "docker", "description": "Nginx reverse proxy config", "priority": 4},
                    # CI/CD and Deployment Scripts
                    {"path": ".github/workflows/deploy.yml", "type": "cicd", "description": "GitHub Actions multi-cloud deployment", "priority": 5},
                    {"path": ".github/workflows/test.yml", "type": "cicd", "description": "Automated testing pipeline", "priority": 5},
                    {"path": "scripts/deploy.sh", "type": "script", "description": "Universal deployment script", "priority": 5},
                    {"path": "scripts/deploy-aws.sh", "type": "script", "description": "AWS ECS deployment script", "priority": 5},
                    {"path": "scripts/deploy-gcp.sh", "type": "script", "description": "Google Cloud deployment script", "priority": 5},
                    {"path": "scripts/deploy-azure.sh", "type": "script", "description": "Azure deployment script", "priority": 5},
                    {"path": "scripts/build-and-push.sh", "type": "script", "description": "Docker build and registry push", "priority": 5},
                    {"path": "scripts/run-migrations.sh", "type": "script", "description": "Database migration script", "priority": 5},
                    # API Testing and Documentation
                    {"path": "tests/unit/auth.test.js", "type": "test", "description": "Authentication unit tests", "priority": 6},
                    {"path": "tests/unit/users.test.js", "type": "test", "description": "User management unit tests", "priority": 6},
                    {"path": "tests/integration/api.test.js", "type": "test", "description": "API integration tests", "priority": 6},
                    {"path": "tests/load/load-test.js", "type": "test", "description": "Load testing configuration", "priority": 6},
                    {"path": "tests/setup.js", "type": "test", "description": "Test environment setup", "priority": 6},
                    {"path": "api/openapi.yaml", "type": "api", "description": "OpenAPI 3.0 specification", "priority": 6},
                    {"path": "api/postman_collection.json", "type": "api", "description": "Postman API test collection", "priority": 6},
                    {"path": "api/insomnia_workspace.json", "type": "api", "description": "Insomnia REST client workspace", "priority": 6},
                    {"path": "api/swagger-ui/index.html", "type": "api", "description": "Swagger UI documentation", "priority": 6},
                    # Configuration and documentation
                    {"path": ".env.example", "type": "config", "description": "Environment variables", "priority": 6},
                    {"path": "README.md", "type": "docs", "description": "API documentation", "priority": 7},
                    {"path": "docs/API.md", "type": "docs", "description": "API endpoints documentation", "priority": 7}
                ],
                "folders": ["src", "src/routes", "src/controllers", "src/models", "src/middleware", "src/config", 
                           "src/utils", "src/services", "src/migrations", "src/seeders",
                           "infrastructure/terraform/aws", "infrastructure/terraform/gcp", "infrastructure/terraform/azure",
                           "infrastructure/cloudformation", "infrastructure/gcp", "infrastructure/azure",
                           "infrastructure/kubernetes", 
                           "docker/aws", "docker/gcp", "docker/azure", "docker/nginx",
                           "tests/unit", "tests/integration", "tests/load",
                           "api", "api/swagger-ui",
                           ".github/workflows", "scripts", "docs"],
                "docker_needed": True,
                "database": "sqlite",
                "api_endpoints": 8,
                "complexity": "medium"
            }
        else:
            return {
                "project_type": "cli",
                "tech_stack": ["nodejs", "commander"],
                "description": f"Command-line tool: {description}",
                "files": [
                    {"path": "src/cli.js", "type": "cli", "description": "Main CLI interface", "priority": 1},
                    {"path": "package.json", "type": "config", "description": "Dependencies", "priority": 1},
                    {"path": "README.md", "type": "docs", "description": "Usage documentation", "priority": 2}
                ],
                "folders": ["src", "bin", "tests"],
                "docker_needed": False,
                "database": None,
                "api_endpoints": 0,
                "complexity": "low"
            }
            
    async def _display_project_plan(self, plan: dict) -> None:
        """Display the project generation plan to the user."""
        console.print(f"\n📋 Project Plan: {plan.get('description', 'Generated project')}")
        
        # Project overview
        overview_table = Table(title="Project Overview", box=ROUNDED, show_header=True)
        overview_table.add_column("Attribute", style="bold #0088FF", width=15)
        overview_table.add_column("Value", style="white")
        
        overview_table.add_row("Type", plan.get('project_type', 'Unknown'))
        overview_table.add_row("Tech Stack", ", ".join(plan.get('tech_stack', [])))
        overview_table.add_row("Complexity", plan.get('complexity', 'Medium').title())
        overview_table.add_row("Docker", "✅ Yes" if plan.get('docker_needed') else "❌ No")
        if plan.get('database'):
            overview_table.add_row("Database", plan['database'])
        overview_table.add_row("Files", str(len(plan.get('files', []))))
        
        console.print(overview_table)
        console.print()
        
        # File structure
        files_table = Table(title="Files to Generate", box=ROUNDED, show_header=True)
        files_table.add_column("Priority", width=8, style="dim")
        files_table.add_column("Path", style="bold #0088FF", width=30)
        files_table.add_column("Type", width=10, style="yellow")
        files_table.add_column("Description", style="white")
        
        # Sort files by priority
        files = sorted(plan.get('files', []), key=lambda x: x.get('priority', 99))
        
        for file_info in files:
            priority = f"P{file_info.get('priority', '?')}"
            files_table.add_row(
                priority,
                file_info.get('path', ''),
                file_info.get('type', '').upper(),
                file_info.get('description', '')
            )
            
        console.print(files_table)
        
    async def _execute_project_generation(self, plan: dict, output_dir: str) -> bool:
        """Execute the complete project generation."""
        try:
            from pathlib import Path
            import os
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            console.print(f"\n🏗️ Creating project structure...")
            
            # Create folder structure
            for folder in plan.get('folders', []):
                folder_path = output_path / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                console.print(f"📁 Created: {folder}")
                
            console.print(f"\n🔨 Generating {len(plan['files'])} files...")
            
            # Generate files in priority order
            files = sorted(plan.get('files', []), key=lambda x: x.get('priority', 99))
            
            for i, file_info in enumerate(files, 1):
                file_path = file_info['path']
                file_type = file_info.get('type', 'unknown')
                description = file_info.get('description', '')
                
                console.print(f"📝 [{i}/{len(files)}] Generating {file_path}...")
                
                # Generate file content using AI
                content = await self._generate_file_content(file_info, plan)
                
                if content:
                    # Save file
                    full_path = output_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    console.print(f"  ✅ {file_path} ({len(content)} chars)")
                else:
                    console.print(f"  ⚠️ Failed to generate {file_path}", style="yellow")
                    
            # Generate Docker files if needed
            if plan.get('docker_needed'):
                await self._generate_docker_files(plan, output_path)
                
            return True
            
        except Exception as e:
            console.print(f"Error during project generation: {e}", style="red")
            return False
            
    async def _generate_file_content(self, file_info: dict, plan: dict) -> str:
        """Generate content for a specific file using AI."""
        if not self.backend:
            return ""
            
        file_path = file_info['path']
        file_type = file_info.get('type', '')
        description = file_info.get('description', '')
        
        # Create specialized prompts based on file type
        if file_type == 'backend':
            prompt = self._create_backend_prompt(file_info, plan)
        elif file_type == 'frontend':
            prompt = self._create_frontend_prompt(file_info, plan)
        elif file_type == 'config':
            prompt = self._create_config_prompt(file_info, plan)
        elif file_type == 'docker':
            prompt = self._create_docker_prompt(file_info, plan)
        elif file_type == 'docs':
            prompt = self._create_docs_prompt(file_info, plan)
        elif file_type == 'iac':
            prompt = self._create_iac_prompt(file_info, plan)
        elif file_type == 'cicd':
            prompt = self._create_cicd_prompt(file_info, plan)
        elif file_type == 'script':
            prompt = self._create_script_prompt(file_info, plan)
        elif file_type == 'test':
            prompt = self._create_test_prompt(file_info, plan)
        elif file_type == 'api':
            prompt = self._create_api_docs_prompt(file_info, plan)
        else:
            prompt = self._create_generic_prompt(file_info, plan)
            
        try:
            conversation = self.backend.chat(self.current_model)
            response = await conversation.send(prompt)
            
            # Extract code from response
            from ..types.models import extract_code
            code = extract_code(response.full_output)
            return code if code else response.full_output.strip()
            
        except Exception as e:
            console.print(f"  Error generating {file_path}: {e}", style="red")
            return ""
            
    def _create_backend_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for backend files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        database = plan.get('database', 'none')
        
        return f"""
        Generate a production-ready {file_info['path']} file for this project:
        
        Project: {plan.get('description', 'Backend service')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'Backend component')}
        Tech Stack: {tech_stack}
        Database: {database}
        API Endpoints: {plan.get('api_endpoints', 'several')}
        
        Requirements:
        - Production-ready code with error handling
        - Proper imports and dependencies
        - RESTful API design if applicable
        - Database integration if needed
        - Environment variable support
        - Proper logging and middleware
        - CORS support for web apps
        
        Generate only the complete code file, no explanations.
        """
        
    def _create_frontend_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for frontend files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        
        return f"""
        Generate a production-ready {file_info['path']} file for this frontend project:
        
        Project: {plan.get('description', 'Frontend application')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'Frontend component')}
        Tech Stack: {tech_stack}
        
        Requirements:
        - Modern React/frontend best practices
        - Responsive design
        - Proper component structure
        - State management
        - API integration ready
        - Error boundary handling
        - Proper imports and exports
        - Clean, maintainable code
        
        Generate only the complete code file, no explanations.
        """
        
    def _create_config_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for configuration files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        
        return f"""
        Generate a production-ready {file_info['path']} configuration file:
        
        Project: {plan.get('description', 'Application')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'Configuration')}
        Tech Stack: {tech_stack}
        
        Requirements:
        - All necessary dependencies for the tech stack
        - Proper scripts for development and production
        - Security best practices
        - Environment-specific configurations
        - Linting and formatting tools
        
        Generate only the complete configuration file, no explanations.
        """
        
    def _create_docker_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for Docker files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        
        return f"""
        Generate a production-ready {file_info['path']} Docker configuration:
        
        Project: {plan.get('description', 'Application')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'Container configuration')}
        Tech Stack: {tech_stack}
        Database: {plan.get('database', 'none')}
        
        Requirements:
        - Multi-stage builds for efficiency
        - Security best practices
        - Proper port exposure
        - Environment variable support
        - Health checks
        - Non-root user
        - Optimized layers
        
        Generate only the complete Docker file, no explanations.
        """
        
    def _create_docs_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for documentation files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        
        return f"""
        Generate comprehensive documentation for {file_info['path']}:
        
        Project: {plan.get('description', 'Application')}
        File: {file_info['path']}
        Tech Stack: {tech_stack}
        Docker: {'Yes' if plan.get('docker_needed') else 'No'}
        Database: {plan.get('database', 'none')}
        
        Requirements:
        - Clear project description and features
        - Installation and setup instructions
        - Usage examples and API documentation
        - Development workflow
        - Docker instructions if applicable
        - Troubleshooting section
        - Contributing guidelines
        - License information
        
        Generate complete markdown documentation.
        """
        
    def _create_generic_prompt(self, file_info: dict, plan: dict) -> str:
        """Create generic AI prompt for other file types."""
        return f"""
        Generate a production-ready {file_info['path']} file:
        
        Project: {plan.get('description', 'Application')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'Project component')}
        Tech Stack: {", ".join(plan.get('tech_stack', []))}
        
        Generate complete, production-ready code following best practices.
        """
        
    def _create_iac_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for Infrastructure as Code files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        file_path = file_info['path']
        
        # Determine the IaC tool and cloud provider from file path
        if 'terraform' in file_path:
            iac_tool = 'Terraform'
            if 'aws' in file_path.lower():
                cloud_provider = 'AWS'
            elif 'gcp' in file_path.lower() or 'google' in file_path.lower():
                cloud_provider = 'Google Cloud'
            elif 'azure' in file_path.lower():
                cloud_provider = 'Azure'
            else:
                cloud_provider = 'Multi-cloud (AWS, Google Cloud, Azure)'
        elif 'cloudformation' in file_path:
            iac_tool = 'CloudFormation'
            cloud_provider = 'AWS'
        elif 'arm-template' in file_path or ('azure' in file_path.lower() and '.json' in file_path):
            iac_tool = 'Azure ARM Template'
            cloud_provider = 'Microsoft Azure'
        elif 'deployment-manager' in file_path or ('gcp' in file_path.lower() and '.yaml' in file_path):
            iac_tool = 'Google Cloud Deployment Manager'
            cloud_provider = 'Google Cloud Platform'
        elif 'kubernetes' in file_path or 'k8s' in file_path:
            iac_tool = 'Kubernetes'
            cloud_provider = 'Kubernetes (cloud-agnostic)'
        else:
            iac_tool = 'Infrastructure as Code'
            cloud_provider = 'Multi-cloud'
            
        return f"""
        Generate production-ready {iac_tool} configuration for {file_info['path']}:
        
        Project: {plan.get('description', 'Application infrastructure')}
        File: {file_path}
        Purpose: {file_info.get('description', 'Infrastructure definition')}
        Tech Stack: {tech_stack}
        Cloud Provider: {cloud_provider}
        Database: {plan.get('database', 'none')}
        
        Requirements:
        - Production-ready infrastructure code
        - Security best practices and compliance
        - High availability and fault tolerance
        - Auto-scaling capabilities where applicable
        - Network security with proper VPC/VNet setup
        - Load balancing and health checks
        - Monitoring and logging integration
        - Cost optimization considerations
        - Environment-specific variables
        - Proper resource tagging and naming
        
        For multi-cloud: Include examples for AWS, Google Cloud, and Azure.
        For single cloud: Focus on that provider's best practices.
        
        Generate only the complete infrastructure code, no explanations.
        """
        
    def _create_cicd_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for CI/CD files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        
        return f"""
        Generate production-ready CI/CD pipeline for {file_info['path']}:
        
        Project: {plan.get('description', 'Application')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'CI/CD pipeline')}
        Tech Stack: {tech_stack}
        Database: {plan.get('database', 'none')}
        
        Requirements:
        - Multi-stage pipeline (build, test, deploy)
        - Environment-specific deployments (dev, staging, prod)
        - Security scanning and vulnerability checks
        - Code quality gates and testing
        - Docker image building and pushing
        - Infrastructure deployment automation
        - Rollback capabilities
        - Notification and monitoring integration
        - Secret management
        - Multi-cloud deployment support (AWS, GCP, Azure)
        
        Generate complete CI/CD pipeline configuration.
        """
        
    def _create_script_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for deployment and setup scripts."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        
        return f"""
        Generate production-ready deployment script for {file_info['path']}:
        
        Project: {plan.get('description', 'Application')}
        File: {file_info['path']}
        Purpose: {file_info.get('description', 'Deployment script')}
        Tech Stack: {tech_stack}
        Database: {plan.get('database', 'none')}
        
        Requirements:
        - Cross-platform compatibility (Linux, macOS, Windows)
        - Environment validation and prerequisites check
        - Error handling and logging
        - Rollback capabilities
        - Multi-cloud support (AWS, Google Cloud, Azure)
        - Docker and Kubernetes integration
        - Database migration and seeding
        - Configuration validation
        - Health checks and verification
        - Interactive prompts with sensible defaults
        
        Generate complete, production-ready script with proper error handling.
        """
        
    def _create_test_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for test files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        file_path = file_info['path']
        
        # Determine test type from path
        if 'unit' in file_path:
            test_type = 'Unit Tests'
            test_focus = 'individual functions and components'
        elif 'integration' in file_path:
            test_type = 'Integration Tests'
            test_focus = 'API endpoints and database interactions'
        elif 'load' in file_path:
            test_type = 'Load Tests'
            test_focus = 'performance and scalability'
        else:
            test_type = 'Tests'
            test_focus = 'application functionality'
            
        return f"""
        Generate comprehensive {test_type.lower()} for {file_info['path']}:
        
        Project: {plan.get('description', 'Application')}
        File: {file_path}
        Purpose: {file_info.get('description', test_type)}
        Test Type: {test_type}
        Test Focus: {test_focus}
        Tech Stack: {tech_stack}
        Database: {plan.get('database', 'none')}
        API Endpoints: {plan.get('api_endpoints', 'several')}
        
        Requirements:
        - Comprehensive test coverage for critical functionality
        - Test setup and teardown with proper cleanup
        - Mock external dependencies and services
        - Clear test descriptions and assertions
        - Error case testing and edge cases
        - Authentication and authorization testing if applicable
        - Database testing with test data isolation
        - API response validation and status code checks
        - Performance benchmarks for load tests
        - Continuous integration compatibility
        
        Generate complete test file with proper test framework setup.
        """
        
    def _create_api_docs_prompt(self, file_info: dict, plan: dict) -> str:
        """Create AI prompt for API documentation files."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        file_path = file_info['path']
        
        # Determine documentation type from file path
        if 'openapi' in file_path or 'swagger' in file_path:
            doc_type = 'OpenAPI 3.0 Specification'
            doc_format = 'YAML'
            doc_purpose = 'complete API specification with schemas and examples'
        elif 'postman' in file_path:
            doc_type = 'Postman Collection'
            doc_format = 'JSON'
            doc_purpose = 'API testing collection with requests and tests'
        elif 'insomnia' in file_path:
            doc_type = 'Insomnia Workspace'
            doc_format = 'JSON'
            doc_purpose = 'REST client workspace with organized requests'
        elif 'swagger-ui' in file_path:
            doc_type = 'Swagger UI HTML'
            doc_format = 'HTML'
            doc_purpose = 'interactive API documentation interface'
        else:
            doc_type = 'API Documentation'
            doc_format = 'Documentation'
            doc_purpose = 'comprehensive API reference'
            
        return f"""
        Generate comprehensive {doc_type} for {file_info['path']}:
        
        Project: {plan.get('description', 'API Service')}
        File: {file_path}
        Purpose: {file_info.get('description', doc_type)}
        Documentation Type: {doc_type}
        Format: {doc_format}
        Focus: {doc_purpose}
        Tech Stack: {tech_stack}
        Database: {plan.get('database', 'none')}
        API Endpoints: {plan.get('api_endpoints', 8)}
        
        Requirements:
        - Complete API endpoint documentation with all HTTP methods
        - Request/response schemas with data types and examples
        - Authentication and authorization requirements
        - Error response codes and error handling examples
        - Rate limiting and usage guidelines
        - Environment variables and configuration options
        - Sample requests and responses for all endpoints
        - Data validation rules and constraints
        - API versioning information if applicable
        - Interactive examples that can be tested directly
        
        For OpenAPI: Include detailed schemas, security definitions, and examples
        For Postman: Include pre-request scripts, tests, and environment variables
        For Insomnia: Include organized folders, environments, and request templates
        For Swagger UI: Include fully functional interactive documentation
        
        Generate complete, production-ready API documentation.
        """
        
    async def _generate_docker_files(self, plan: dict, output_path) -> None:
        """Generate additional Docker files if needed."""
        try:
            console.print("\n🐳 Generating Docker configuration...")
            
            # Generate Dockerfile if not already in plan
            dockerfile_exists = any(f['path'] == 'Dockerfile' for f in plan.get('files', []))
            if not dockerfile_exists:
                dockerfile_info = {
                    'path': 'Dockerfile',
                    'type': 'docker',
                    'description': 'Main container configuration'
                }
                content = await self._generate_file_content(dockerfile_info, plan)
                if content:
                    with open(output_path / 'Dockerfile', 'w', encoding='utf-8') as f:
                        f.write(content)
                    console.print("  ✅ Dockerfile")
                    
            # Generate .dockerignore
            dockerignore_content = self._create_dockerignore_content(plan)
            with open(output_path / '.dockerignore', 'w', encoding='utf-8') as f:
                f.write(dockerignore_content)
            console.print("  ✅ .dockerignore")
            
            # Generate docker-compose.yml if it's a web app
            if plan.get('project_type') == 'web_app':
                compose_info = {
                    'path': 'docker-compose.yml',
                    'type': 'docker',
                    'description': 'Docker Compose orchestration'
                }
                content = await self._generate_file_content(compose_info, plan)
                if content:
                    with open(output_path / 'docker-compose.yml', 'w', encoding='utf-8') as f:
                        f.write(content)
                    console.print("  ✅ docker-compose.yml")
                    
        except Exception as e:
            console.print(f"Error generating Docker files: {e}", style="red")
            
    def _create_dockerignore_content(self, plan: dict) -> str:
        """Create .dockerignore content based on project type."""
        base_ignore = [
            "node_modules",
            "npm-debug.log",
            ".git",
            ".gitignore",
            "README.md",
            ".env",
            ".env.local",
            ".env.development",
            ".env.test",
            ".env.production",
            "coverage",
            ".nyc_output",
            "*.log",
            "logs",
            "*.md",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        # Add project-specific ignores
        if 'react' in plan.get('tech_stack', []):
            base_ignore.extend([
                "build",
                "dist",
                ".cache"
            ])
            
        return "\n".join(base_ignore) + "\n"
        
    async def _display_next_steps(self, output_dir: str, plan: dict) -> None:
        """Display next steps for the user."""
        console.print("\n🚀 Next Steps:")
        
        steps_table = Table(title="Getting Started", box=ROUNDED, show_header=False)
        steps_table.add_column("Step", style="bold #0088FF", width=4)
        steps_table.add_column("Action", style="white")
        
        # Navigate to directory
        steps_table.add_row("1.", f"cd {output_dir}")
        
        # Install dependencies
        if 'nodejs' in plan.get('tech_stack', []):
            if plan.get('project_type') == 'web_app':
                steps_table.add_row("2.", "Install backend: cd backend && npm install")
                steps_table.add_row("3.", "Install frontend: cd ../frontend && npm install")
            else:
                steps_table.add_row("2.", "Install dependencies: npm install")
        
        # Docker instructions
        if plan.get('docker_needed'):
            if plan.get('project_type') == 'web_app' and any(f['path'] == 'docker-compose.yml' for f in plan.get('files', [])):
                steps_table.add_row("4.", "Start with Docker: docker-compose up --build")
            else:
                steps_table.add_row("4.", "Build Docker image: docker build -t my-app .")
                steps_table.add_row("5.", "Run container: docker run -p 3000:3000 my-app")
        else:
            if plan.get('project_type') == 'web_app':
                steps_table.add_row("4.", "Start backend: cd backend && npm start")
                steps_table.add_row("5.", "Start frontend: cd frontend && npm start")
            else:
                steps_table.add_row("4.", "Start application: npm start")
                
        # Read documentation
        steps_table.add_row("ℹ️", "Read README.md for detailed instructions")
        
        console.print(steps_table)
        
        # Show URLs if it's a web app
        if plan.get('project_type') == 'web_app':
            console.print("\n🌐 Default URLs:")
            console.print("  Frontend: http://localhost:3000")
            console.print("  Backend API: http://localhost:8000")
            
        # Offer to build Docker images
        if plan.get('docker_needed'):
            if Confirm.ask("\n🐳 Build Docker images now?", default=True):
                await self._build_docker_images(output_dir, plan)
        
        # Offer to open the directory
        if Confirm.ask("\n📁 Open project directory in file explorer?", default=True):
            import subprocess
            import os
            
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', output_dir])
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(['open', output_dir])  # macOS
                    # subprocess.run(['xdg-open', output_dir])  # Linux
                console.print(f"📁 Opened {output_dir}")
            except Exception as e:
                console.print(f"Could not open directory: {e}", style="yellow")
                
    async def _generate_architecture_diagram(self, plan: Dict, project_description: str) -> Optional[Dict]:
        """Generate React Flow architecture diagram using Groq AI."""
        import json
        import tempfile
        import webbrowser
        import http.server
        import socketserver
        import threading
        from rich.prompt import Confirm
        
        console.print("\n🎨 Generating system architecture diagram...", style="bold blue")
        
        # Create detailed prompt for architecture diagram generation
        architecture_prompt = self._create_architecture_diagram_prompt(plan, project_description)
        
        try:
            # Get Groq backend from config
            if not self.config or not hasattr(self.config, 'backends') or 'groq' not in self.config.backends:
                console.print("❌ Groq backend not configured. Skipping architecture diagram.", style="yellow")
                return None
                
            groq_config = self.config.backends['groq']
            if not groq_config.api_key or groq_config.api_key.startswith('$'):
                console.print("❌ Groq API key not set. Skipping architecture diagram.", style="yellow")
                return None
            
            # Import and configure Groq backend
            from ..backends.groq import GroqBackend
            groq_backend = GroqBackend(api_key=groq_config.api_key)
            groq_backend.set_json_mode(True)  # Enable JSON response format
            
            # Generate architecture diagram
            system_message = Message(role="system", content="You are a system architecture expert. Generate detailed React Flow architecture diagrams as JSON.")
            conversation = groq_backend.chat(
                groq_config.default_model or "meta-llama/llama-3.1-70b-versatile",
                system_message
            )
            
            response = await conversation.send(architecture_prompt)
            
            if not response or not response.full_output:
                console.print("❌ Failed to generate architecture diagram", style="red")
                return None
            
            # Parse the JSON response
            try:
                diagram_data = json.loads(response.full_output)
                console.print("✅ Architecture diagram generated successfully!", style="green")
                return diagram_data
            except json.JSONDecodeError as e:
                console.print(f"❌ Invalid JSON in architecture response: {e}", style="red")
                return None
                
        except Exception as e:
            console.print(f"❌ Error generating architecture diagram: {e}", style="red")
            return None
    
    def _create_architecture_diagram_prompt(self, plan: Dict, project_description: str) -> str:
        """Create detailed prompt for React Flow architecture diagram generation."""
        tech_stack = ", ".join(plan.get('tech_stack', []))
        project_type = plan.get('project_type', 'application')
        database = plan.get('database', 'none')
        
        return f"""
        Generate a comprehensive system architecture diagram for the following project using React Flow JSON format.
        
        PROJECT DETAILS:
        Description: {project_description}
        Type: {project_type}
        Technology Stack: {tech_stack}
        Database: {database}
        Number of Files: {len(plan.get('files', []))}
        Docker Needed: {plan.get('docker_needed', False)}
        
        REQUIREMENTS:
        1. Create a React Flow compatible JSON structure with nodes and edges
        2. Include all major system components (frontend, backend, database, external services)
        3. Show data flow and communication patterns between components
        4. Include infrastructure components (load balancers, caches, CDN if applicable)
        5. Add security components (authentication, API gateways)
        6. Use proper node types and positioning for clear visualization
        
        NODE TYPES TO USE:
        - 'frontend': Web applications, mobile apps, user interfaces
        - 'api-service': Backend APIs, microservices, server applications
        - 'database': SQL/NoSQL databases, data stores
        - 'authentication': Auth services, identity providers, JWT systems
        - 'cache': Redis, Memcached, application caches
        - 'queue': Message queues, event buses, pub/sub systems
        - 'load-balancer': Load balancers, reverse proxies
        - 'api-gateway': API gateways, service mesh entry points
        - 'cdn': Content delivery networks
        - 'external-service': Third-party APIs, external integrations
        - 'monitoring': Logging, metrics, monitoring services
        - 'storage': File storage, blob storage, media storage
        
        EXAMPLE JSON FORMAT:
        {{
            "nodes": [
                {{
                    "id": "frontend-1",
                    "type": "frontend", 
                    "position": {{ "x": 100, "y": 100 }},
                    "data": {{
                        "name": "React Web App",
                        "description": "Main user interface",
                        "technology": "React.js",
                        "color": "#3b82f6"
                    }}
                }},
                {{
                    "id": "api-1",
                    "type": "api-service",
                    "position": {{ "x": 400, "y": 100 }},
                    "data": {{
                        "name": "REST API",
                        "description": "Main backend service",
                        "technology": "Node.js/Express",
                        "color": "#10b981"
                    }}
                }}
            ],
            "edges": [
                {{
                    "id": "frontend-api",
                    "source": "frontend-1",
                    "target": "api-1",
                    "type": "smoothstep",
                    "label": "HTTPS API calls",
                    "data": {{
                        "protocol": "HTTPS",
                        "security": "JWT Auth"
                    }}
                }}
            ],
            "metadata": {{
                "title": "System Architecture",
                "description": "High-level system architecture overview",
                "version": "1.0",
                "created_at": "{datetime.now().isoformat()}"
            }}
        }}
        
        POSITIONING GUIDELINES:
        - Frontend components: x: 50-200, y: 50-150
        - API/Backend services: x: 300-500, y: 50-200
        - Databases: x: 600-800, y: 100-250
        - External services: x: 50-150, y: 300-400
        - Infrastructure (LB, CDN): x: 200-400, y: 300-400
        - Monitoring/Logging: x: 500-700, y: 300-400
        
        Generate a comprehensive architecture diagram that accurately represents this {project_type} project with {tech_stack} technology stack. Return ONLY the JSON structure, no additional text or explanations.
        """
    
    async def _show_architecture_preview(self, diagram_data: Dict) -> bool:
        """Show architecture diagram preview in browser and get user approval."""
        import json
        import tempfile
        import webbrowser
        import http.server
        import socketserver
        import threading
        import time
        from pathlib import Path
        
        console.print("\n🌐 Opening architecture diagram preview...", style="bold blue")
        
        # Create HTML page with React Flow diagram
        html_content = self._create_react_flow_html(diagram_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            # Open in browser
            webbrowser.open(f'file://{temp_file}')
            
            console.print("\n📋 Architecture Diagram Preview Opened", style="bold green")
            console.print("\n📊 Diagram Details:", style="bold")
            
            # Show diagram statistics
            nodes_count = len(diagram_data.get('nodes', []))
            edges_count = len(diagram_data.get('edges', []))
            
            stats_table = Table(show_header=False, box=None)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Components", str(nodes_count))
            stats_table.add_row("Connections", str(edges_count))
            stats_table.add_row("Architecture Type", diagram_data.get('metadata', {}).get('title', 'System Architecture'))
            
            console.print(stats_table)
            
            # Get user approval
            console.print("\n🔍 Please review the architecture diagram in your browser.", style="bold yellow")
            
            while True:
                choice = Prompt.ask(
                    "\nDo you approve this architecture?",
                    choices=["approve", "regenerate", "modify", "skip"],
                    default="approve"
                )
                
                if choice == "approve":
                    console.print("✅ Architecture approved! Proceeding with code generation...", style="green")
                    return True
                elif choice == "regenerate":
                    console.print("🔄 Regenerating architecture diagram...", style="yellow")
                    return False  # Signal to regenerate
                elif choice == "modify":
                    feedback = Prompt.ask(
                        "\nWhat changes would you like to the architecture?",
                        default="Add more components and improve security"
                    )
                    console.print(f"✏️ Modifications requested: {feedback}", style="cyan")
                    console.print("🔄 Regenerating with your feedback...", style="yellow")
                    # Store feedback for next regeneration (could be implemented in future)
                    return False  # Signal to regenerate with feedback
                elif choice == "skip":
                    console.print("⏭️ Skipping architecture preview. Proceeding with code generation...", style="yellow")
                    return True
                    
        finally:
            # Clean up temporary file
            try:
                Path(temp_file).unlink()
            except Exception:
                pass
    
    def _create_react_flow_html(self, diagram_data: Dict) -> str:
        """Create HTML page with React Flow diagram visualization."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SnapInfra - System Architecture Preview</title>
            <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
            <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
            <script src="https://unpkg.com/@xyflow/react@12/dist/umd/index.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/@xyflow/react@12/dist/style.css" />
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #fafafa;
                }}
                .header {{
                    background: white;
                    padding: 1rem 2rem;
                    border-bottom: 1px solid #e5e5e5;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .header h1 {{
                    margin: 0;
                    color: #1a1a1a;
                    font-size: 1.5rem;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 0.5rem 0 0 0;
                    color: #666;
                    font-size: 0.875rem;
                }}
                .stats {{
                    display: flex;
                    gap: 1rem;
                    margin-top: 0.5rem;
                }}
                .stat {{
                    background: #f8f9fa;
                    padding: 0.25rem 0.5rem;
                    border-radius: 0.375rem;
                    font-size: 0.75rem;
                    color: #374151;
                    border: 1px solid #e5e7eb;
                }}
                .diagram-container {{
                    height: calc(100vh - 120px);
                    position: relative;
                }}
                .react-flow__node-default {{
                    background: white;
                    border: 2px solid #e5e5e5;
                    border-radius: 8px;
                    padding: 10px;
                    min-width: 150px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .node-title {{
                    font-weight: 600;
                    font-size: 14px;
                    color: #1a1a1a;
                    margin-bottom: 4px;
                }}
                .node-description {{
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 4px;
                }}
                .node-technology {{
                    font-size: 11px;
                    color: #888;
                    font-style: italic;
                }}
                .approval-panel {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    border: 1px solid #e5e5e5;
                }}
                .approval-text {{
                    margin: 0 0 0.5rem 0;
                    font-size: 14px;
                    font-weight: 500;
                    color: #1a1a1a;
                }}
                .cli-instruction {{
                    font-size: 12px;
                    color: #666;
                    font-family: 'SF Mono', Monaco, monospace;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏗️ System Architecture Preview</h1>
                <p>{diagram_data.get('metadata', {}).get('description', 'Generated system architecture diagram')}</p>
                <div class="stats">
                    <span class="stat">📦 {len(diagram_data.get('nodes', []))} Components</span>
                    <span class="stat">🔗 {len(diagram_data.get('edges', []))} Connections</span>
                    <span class="stat">🤖 AI Generated</span>
                </div>
            </div>
            <div id="diagram-root" class="diagram-container"></div>
            
            <div class="approval-panel">
                <p class="approval-text">Review the architecture in your terminal</p>
                <p class="cli-instruction">Return to SnapInfra CLI to approve/modify</p>
            </div>
            
            <script>
                const {{ useState, useCallback, useMemo }} = React;
                const {{ ReactFlow, Controls, MiniMap, Background, BackgroundVariant }} = ReactFlowLib;
                
                const diagramData = {json.dumps(diagram_data, indent=2)};
                
                const nodeTypes = {{
                    'frontend': CustomNode,
                    'api-service': CustomNode,
                    'database': CustomNode,
                    'authentication': CustomNode,
                    'cache': CustomNode,
                    'queue': CustomNode,
                    'load-balancer': CustomNode,
                    'api-gateway': CustomNode,
                    'cdn': CustomNode,
                    'external-service': CustomNode,
                    'monitoring': CustomNode,
                    'storage': CustomNode
                }};
                
                function CustomNode({{ data }}) {{
                    const nodeColor = data.color || '#3b82f6';
                    const nodeStyle = {{
                        background: 'white',
                        border: `2px solid ${{nodeColor}}`,
                        borderRadius: '8px',
                        padding: '12px',
                        minWidth: '160px',
                        textAlign: 'center',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }};
                    
                    return React.createElement('div', {{ style: nodeStyle }}, [
                        React.createElement('div', {{ className: 'node-title', key: 'title' }}, data.name),
                        React.createElement('div', {{ className: 'node-description', key: 'desc' }}, data.description),
                        data.technology && React.createElement('div', {{ className: 'node-technology', key: 'tech' }}, data.technology)
                    ]);
                }}
                
                function ArchitectureDiagram() {{
                    const nodes = diagramData.nodes || [];
                    const edges = diagramData.edges || [];
                    
                    // Enhanced edge styling
                    const styledEdges = edges.map(edge => ({{
                        ...edge,
                        type: edge.type || 'smoothstep',
                        animated: true,
                        style: {{
                            stroke: '#6b7280',
                            strokeWidth: 2
                        }},
                        markerEnd: {{
                            type: 'arrowclosed',
                            width: 20,
                            height: 20,
                            color: '#6b7280'
                        }},
                        labelStyle: {{
                            fontSize: '12px',
                            fontWeight: '500',
                            fill: '#374151'
                        }}
                    }}));
                    
                    return React.createElement(ReactFlow, {{
                        nodes: nodes,
                        edges: styledEdges,
                        nodeTypes: nodeTypes,
                        fitView: true,
                        fitViewOptions: {{ padding: 0.2 }},
                        minZoom: 0.1,
                        maxZoom: 2,
                        defaultViewport: {{ x: 0, y: 0, zoom: 1 }}
                    }}, [
                        React.createElement(Background, {{ 
                            key: 'bg',
                            variant: BackgroundVariant.Dots,
                            gap: 16,
                            size: 0.8,
                            color: '#d1d5db'
                        }}),
                        React.createElement(Controls, {{ 
                            key: 'controls',
                            position: 'bottom-right' 
                        }}),
                        React.createElement(MiniMap, {{
                            key: 'minimap', 
                            position: 'bottom-left',
                            pannable: true,
                            zoomable: true
                        }})
                    ]);
                }}
                
                const root = ReactDOM.createRoot(document.getElementById('diagram-root'));
                root.render(React.createElement(ArchitectureDiagram));
            </script>
        </body>
        </html>
        """
    
    async def _build_docker_images(self, project_dir: str, plan: Dict) -> None:
        """Build Docker images for the generated project."""
        import subprocess
        import os
        
        console.print("\n🔨 Building Docker images...", style="bold blue")
        
        # Check for docker-compose.yml first
        docker_compose_path = os.path.join(project_dir, 'docker-compose.yml')
        dockerfile_path = os.path.join(project_dir, 'Dockerfile')
        
        try:
            if os.path.exists(docker_compose_path):
                # Use docker-compose build
                console.print("📋 Found docker-compose.yml, building services...")
                result = subprocess.run(
                    ['docker-compose', 'build'], 
                    cwd=project_dir, 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    console.print("✅ Docker images built successfully!", style="green")
                    console.print("\n💡 To start the services, run: docker-compose up", style="cyan")
                else:
                    console.print(f"❌ Build failed: {result.stderr}", style="red")
                    
            elif os.path.exists(dockerfile_path):
                # Use docker build
                project_name = os.path.basename(project_dir).lower().replace(' ', '-')
                console.print(f"🐳 Found Dockerfile, building image '{project_name}'...")
                
                result = subprocess.run(
                    ['docker', 'build', '-t', project_name, '.'], 
                    cwd=project_dir, 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    console.print("✅ Docker image built successfully!", style="green")
                    console.print(f"\n💡 To run the container, use: docker run -p 8080:8080 {project_name}", style="cyan")
                else:
                    console.print(f"❌ Build failed: {result.stderr}", style="red")
                    
            else:
                console.print("❌ No Docker files found to build", style="yellow")
                
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Docker build error: {e}", style="red")
        except FileNotFoundError:
            console.print("❌ Docker not found. Please install Docker first.", style="red")
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}", style="red")
    
    def _is_project_description(self, user_input: str) -> bool:
        """Detect if user input describes a project that should trigger comprehensive generation."""
        # Convert to lowercase for analysis
        text = user_input.lower()
        
        # Project indicators
        project_indicators = [
            'app', 'application', 'website', 'web app', 'webapp', 'platform', 'service', 
            'system', 'tool', 'cli', 'dashboard', 'portal', 'api', 'backend', 'frontend',
            'project', 'build', 'create', 'develop', 'make', 'generate', 'setup'
        ]
        
        # Technology indicators
        tech_indicators = [
            'react', 'nodejs', 'node.js', 'express', 'fastapi', 'flask', 'django', 'vue',
            'angular', 'next.js', 'nuxt', 'docker', 'kubernetes', 'database', 'mongodb',
            'mysql', 'postgres', 'sqlite', 'redis', 'rest api', 'graphql', 'microservice'
        ]
        
        # Function/purpose indicators
        purpose_indicators = [
            'todo', 'task', 'blog', 'ecommerce', 'e-commerce', 'shop', 'store', 'chat',
            'messaging', 'social', 'crm', 'cms', 'booking', 'calendar', 'inventory',
            'management', 'tracking', 'monitoring', 'dashboard', 'analytics', 'auth',
            'login', 'user', 'admin', 'crud', 'portfolio', 'landing'
        ]
        
        # Check for project indicators
        has_project_words = any(indicator in text for indicator in project_indicators)
        has_tech_words = any(indicator in text for indicator in tech_indicators)
        has_purpose_words = any(indicator in text for indicator in purpose_indicators)
        
        # Project description patterns - words that suggest comprehensive projects
        project_patterns = [
            'with', 'using', 'that', 'for', 'to', 'include', 'have', 'feature', 'create', 'build', 'make'
        ]
        has_project_patterns = any(pattern in text for pattern in project_patterns)
        
        # Must have at least one project/tech/purpose word and be reasonably complex
        word_count = len(text.split())
        is_complex_enough = word_count >= 3
        
        # Questions or help requests should not trigger project generation
        question_words = ['how', 'what', 'why', 'when', 'where', 'help', 'explain', 'show', '?']
        is_question = any(word in text for word in question_words)
        
        # Single infrastructure keywords without context should use standard generation
        single_keywords = [
            'terraform', 'cloudformation', 'kubernetes yaml', 'helm chart', 'docker compose',
            'kubernetes deployment', 'k8s deployment', 'deployment yaml'
        ]
        is_single_keyword = any(keyword in text for keyword in single_keywords) and word_count <= 6
        
        # Decision logic
        is_project = (
            is_complex_enough and
            (has_project_words or has_tech_words or has_purpose_words) and
            has_project_patterns and
            not is_question and
            not is_single_keyword
        )
        
        return is_project
        
    def _choose_output_location(self, project_name: str) -> str:
        """Let user choose where to save the generated project."""
        import os
        from pathlib import Path
        
        console.print("\n📁 Where would you like to save your project?")
        
        # Get current directory
        current_dir = os.getcwd()
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
        options = [
            ("1", f"Current directory: {current_option}", current_option),
            ("2", f"Desktop: {desktop_dir}", desktop_dir),
            ("3", "Custom path", "custom")
        ]
        
        for key, description, _ in options:
            console.print(f"  {key}. {description}")
            
        console.print()
        
        while True:
            try:
                choice = Prompt.ask(
                    "Choose location",
                    choices=["1", "2", "3"],
                    default="1"
                )
                
                if choice == "1":
                    return current_option
                elif choice == "2":
                    return desktop_dir
                elif choice == "3":
                    custom_path = Prompt.ask(
                        f"Enter custom path for '{project_name}'",
                        default=f"./{project_name}"
                    )
                    # Ensure the project name is included in the path
                    if not custom_path.endswith(project_name):
                        custom_path = os.path.join(custom_path, project_name)
                    return custom_path
                    
            except (ValueError, KeyboardInterrupt):
                console.print("Invalid choice, please select 1, 2, or 3.", style="yellow")
                continue

    async def select_backend_and_model(self) -> bool:
        """Interactive backend and model selection."""
        if not self.config:
            return False
        
        # Get available backends with valid API keys
        available_backends = []
        for backend_name, backend_config in self.config.backends.items():
            if (backend_config.api_key and 
                backend_config.api_key.strip() and 
                not backend_config.api_key.startswith('$') and  # Reject unresolved env vars
                backend_config.api_key not in ['your-api-key', 'None']):
                available_backends.append((backend_name, backend_config))
        
        if not available_backends:
            console.print(Panel(
                "No backends with API keys found.\n\nPlease add your API keys to the configuration file.",
                title="API Keys Required",
                border_style="red",
                box=SQUARE
            ))
            return False
        
        # Default backend selection
        if self.config.default_backend and self.config.default_backend in [b[0] for b in available_backends]:
            self.current_backend_name = self.config.default_backend
            backend_config = self.config.backends[self.current_backend_name]
        else:
            # Interactive selection
            console.print("🤖 Select AI Backend:")
            for i, (name, config) in enumerate(available_backends, 1):
                model_info = f" ({config.default_model})" if config.default_model else ""
                console.print(f"  {i}. {name}{model_info}")
            
            while True:
                try:
                    choice = Prompt.ask("Choose backend", choices=[str(i) for i in range(1, len(available_backends) + 1)])
                    self.current_backend_name, backend_config = available_backends[int(choice) - 1]
                    break
                except (ValueError, IndexError):
                    console.print("Invalid choice, please try again.", style="red")
        
        # Create backend
        try:
            self.backend = create_backend(backend_config)
            self.current_model = backend_config.default_model
            
            if not self.current_model:
                console.print("🔍 Fetching available models...")
                try:
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                        task = progress.add_task("Loading models...", total=None)
                        models = await self.backend.list_models()
                    
                    if models:
                        console.print("📋 Available models:")
                        for i, model in enumerate(models[:10], 1):  # Show first 10
                            console.print(f"  {i}. {model}")
                        
                        if len(models) > 10:
                            console.print(f"  ... and {len(models) - 10} more")
                        
                        choice = Prompt.ask("Choose model number or press Enter for default", default="1")
                        try:
                            self.current_model = models[int(choice) - 1]
                        except (ValueError, IndexError):
                            self.current_model = models[0]
                    else:
                        console.print("⚠️ No models found, using default", style="yellow")
                        self.current_model = "default"
                except Exception as e:
                    console.print(f"⚠️ Could not fetch models: {e}", style="yellow")
                    self.current_model = "default"
            
            # Initialize model switching support
            await self._initialize_model_switching()
            
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to create backend: {e}", style="red")
            return False
    
    async def _initialize_model_switching(self):
        """Initialize model switching support."""
        try:
            # Store original model and backend for fallback purposes
            self.original_model = self.current_model
            self.original_backend_name = self.current_backend_name
            
            # Get available backends from config
            available_backends = list(self.config.backends.keys())
            
            # Initialize fallback models
            self.fallback_models = model_switcher.get_fallback_models(
                self.current_model,
                self.current_backend_name,
                available_backends
            )
            
            if self.fallback_models:
                console.print(f"✨ Initialized smart model switching with {len(self.fallback_models)} fallback models", style="dim green")
            
        except Exception as e:
            console.print(f"Could not initialize model switching: {e}", style="dim red")
    
    async def _handle_rate_limit_with_switching(self, operation, *args, **kwargs):
        """Handle operations with automatic model switching on rate limits."""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                result = await operation(*args, **kwargs)
                if attempt > 0:
                    console.print(f"✅ Operation succeeded after {attempt} attempts", style="green")
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if any(indicator in error_msg for indicator in ["rate limit", "429", "quota exceeded", "too many requests"]):
                    console.print(f"⚠️ Rate limit hit: {str(e)[:100]}...", style="yellow")
                    
                    # Try switching to a fallback model
                    if attempt < max_attempts - 1:
                        if await self._try_fallback_model():
                            continue
                    
                    # If we're here, no more fallbacks available
                    console.print("❌ No more fallback models available", style="red")
                    raise e
                else:
                    # Non-rate-limit error, don't retry
                    raise e
        
        raise Exception(f"Operation failed after {max_attempts} attempts")
    
    async def _try_fallback_model(self) -> bool:
        """Try switching to the next available fallback model."""
        if self.current_fallback_index >= len(self.fallback_models):
            return False
        
        try:
            new_model, new_backend = self.fallback_models[self.current_fallback_index]
            self.current_fallback_index += 1
            
            # Get backend config
            backend_config = self.config.backends.get(new_backend)
            if not backend_config:
                return False
            
            # Create new backend
            new_backend_instance = create_backend(backend_config)
            
            # Test the new model
            test_models = await new_backend_instance.list_models()
            if new_model not in test_models:
                console.print(f"Model {new_model} not available on {new_backend}", style="yellow")
                return False
            
            # Update to new model/backend
            old_model = self.current_model
            old_backend = self.current_backend_name
            
            self.backend = new_backend_instance
            self.current_model = new_model
            self.current_backend_name = new_backend
            self.model_switches_count += 1
            
            # Show switch explanation
            explanation = model_switcher.explain_model_switch(
                old_model, new_model, old_backend, new_backend, "Rate limit encountered"
            )
            console.print(explanation, style="cyan")
            
            return True
            
        except Exception as e:
            console.print(f"Failed to switch to fallback model: {e}", style="red")
            return False

    def format_ai_response(self, response: Any) -> None:
        """Format and display AI response in clean bubble format."""
        # Get response content
        full_output = response.full_output if hasattr(response, 'full_output') else str(response)
        
        # Display in AI bubble
        self.display_ai_message(full_output)
        
        # Show metadata if available
        if hasattr(response, 'tokens_used') and response.tokens_used:
            metadata = f"Tokens: {response.tokens_used} | Model: {self.current_model}"
            console.print(Text(metadata, style="dim #0088FF"))
            console.print()

    def display_user_message(self, message: str) -> None:
        """Display user message in clean chat bubble format."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # User chat bubble - clean rectangular design
        user_bubble = Panel(
            Text(message, style="white"),
            title=f"You - {timestamp}",
            title_align="left",
            border_style="#0088FF",
            box=SQUARE,  # No rounded corners
            padding=(0, 1),
            width=80
        )
        
        console.print()
        console.print(user_bubble)

    async def handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands like /help, /models, etc. Returns True if command was handled."""
        if not user_input.startswith('/'):
            return False
        
        command = user_input.lower().strip()
        
        if command == '/help':
            self.display_help()
        elif command == '/models':
            await self.display_models()
        elif command == '/switch':
            await self.switch_backend_model()
        elif command == '/keys':
            await self.manage_api_keys()
        elif command == '/settings':
            await self.manage_generation_settings()
        elif command == '/generate':
            await self.generate_comprehensive_project()
        elif command == '/save':
            await self.save_last_response()
        elif command == '/copy':
            self.copy_last_response()
        elif command == '/clear':
            self.clear_conversation()
        elif command == '/history':
            self.display_history()
        elif command == '/examples':
            self.display_examples()
        elif command == '/exit':
            return await self.exit_chat()
        else:
            console.print(f"Unknown enterprise command: {command}", style="red")
            console.print("Type /help to access enterprise command documentation")
        
        return True

    def display_help(self) -> None:
        """Display enterprise help documentation."""
        help_content = Table(title="SnapInfra Enterprise Platform Documentation", box=ROUNDED, title_style="bold #0088FF")
        help_content.add_column("Category", style="bold #0088FF", no_wrap=True)
        help_content.add_column("Enterprise Capabilities", style="white")
        
        help_sections = [
            ("Agentic Project Generation", "Describe any project idea and get complete working files generated instantly\nExample: 'calendar app', 'todo list with React', 'Python web scraper'"),
            ("Intelligent File Creation", "AI analyzes your request and creates all necessary files with actual code\nIncludes config files, README, dependencies, and project structure"),
            ("Available Commands", "Use slash commands for system functions\n/models, /switch, /keys, /save, /copy, /clear, /help, /exit"),
            ("Local Project Output", "All projects are created directly in your current directory\nReady to run with proper dependencies and documentation"),
            ("AI Technology", "Powered by Groq and OpenAI for fast, intelligent code generation\nSupports all major programming languages and frameworks"),
        ]
        
        for category, description in help_sections:
            help_content.add_row(category, description)
        
        console.print(help_content)
        console.print()
        
        # Agentic project examples
        examples_panel = Panel(
            Text.assemble(
                ("Instant Project Generation Examples:\n\n", "bold #0088FF"),
                ("▸ ", "#0088FF"), ("'calendar app' - Creates a full calendar application with UI\n", "white"),
                ("▸ ", "#0088FF"), ("'todo list with React' - Complete React todo app with backend\n", "white"),
                ("▸ ", "#0088FF"), ("'Python web scraper' - Web scraper with all dependencies\n", "white"),
                ("▸ ", "#0088FF"), ("'blog website' - Full blog with CMS and database\n", "white"),
                ("▸ ", "#0088FF"), ("'REST API for user management' - Complete API with auth", "white")
            ),
            title="Project Ideas",
            border_style="#0088FF"
        )
        console.print(examples_panel)

    async def display_models(self) -> None:
        """Display available enterprise AI models."""
        if not self.backend:
            console.print("No enterprise backend selected", style="red")
            return
        
        try:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Retrieving enterprise AI models...", total=None)
                models = await self.backend.list_models()
            
            if models:
                models_table = Table(title=f"Enterprise AI Models - {self.current_backend_name.upper()}", box=ROUNDED, title_style="bold #0088FF")
                models_table.add_column("#", style="dim", width=3)
                models_table.add_column("Enterprise Model", style="#0088FF")
                models_table.add_column("Status", style="white")
                
                for i, model in enumerate(models, 1):
                    status = "Active" if model == self.current_model else "Available"
                    status_style = "bold green" if model == self.current_model else "white"
                    models_table.add_row(str(i), model, Text(status, style=status_style))
                
                console.print(models_table)
            else:
                console.print("No enterprise models available", style="red")
                
        except Exception as e:
            console.print(f"Error retrieving enterprise models: {e}", style="red")

    async def switch_backend_model(self) -> None:
        """Switch enterprise backend or model."""
        console.print("Enterprise Configuration Management", style="bold #0088FF")
        
        choice = Prompt.ask(
            "Select enterprise configuration to modify",
            choices=["backend", "model", "cancel"],
            default="model"
        )
        
        if choice == "cancel":
            return
        elif choice == "backend":
            await self.select_backend_and_model()
        elif choice == "model":
            await self.display_models()
            try:
                models = await self.backend.list_models()
                if models:
                    choice = Prompt.ask("Select enterprise model number", default="1")
                    self.current_model = models[int(choice) - 1]
                    console.print(f"Enterprise model activated: {self.current_model}", style="bold #0088FF")
            except Exception as e:
                console.print(f"Error switching enterprise model: {e}", style="red")

    async def save_last_response(self) -> None:
        """Export enterprise infrastructure to files."""
        if not self.chat_history:
            console.print("No enterprise infrastructure to export", style="red")
            return
        
        # Get last AI response
        last_response = None
        for entry in reversed(self.chat_history):
            if entry['type'] == 'ai':
                last_response = entry
                break
        
        if not last_response:
            console.print("No enterprise infrastructure generated yet", style="red")
            return
        
        # Ask for enterprise export filename
        default_name = f"enterprise_infrastructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        code_file = Prompt.ask("Export infrastructure code to file (or Enter to skip)", default="")
        if code_file:
            try:
                Path(code_file).write_text(last_response['response'].code, encoding='utf-8')
                console.print(f"Infrastructure code exported to: {code_file}", style="bold #0088FF")
            except Exception as e:
                console.print(f"Error exporting infrastructure code: {e}", style="red")
        
        full_file = Prompt.ask("Export complete enterprise documentation (or Enter to skip)", default="")
        if full_file:
            try:
                Path(full_file).write_text(last_response['response'].full_output, encoding='utf-8')
                console.print(f"Enterprise documentation exported to: {full_file}", style="bold #0088FF")
            except Exception as e:
                console.print(f"Error exporting enterprise documentation: {e}", style="red")

    def copy_last_response(self) -> None:
        """Copy enterprise infrastructure to clipboard."""
        if not self.chat_history:
            console.print("No enterprise infrastructure to copy", style="red")
            return
        
        # Get last AI response
        last_response = None
        for entry in reversed(self.chat_history):
            if entry['type'] == 'ai':
                last_response = entry
                break
        
        if not last_response:
            console.print("No enterprise infrastructure generated yet", style="red")
            return
        
        try:
            copy_to_clipboard(last_response['response'].code)
            console.print("Enterprise infrastructure copied to clipboard", style="bold #0088FF")
        except Exception as e:
            console.print(f"Error copying to enterprise clipboard: {e}", style="red")

    def clear_conversation(self) -> None:
        """Clear enterprise session history."""
        if Confirm.ask("Clear enterprise session history?", default=False):
            self.chat_history.clear()
            self.conversation = None
            console.clear()
            console.print("Enterprise session cleared", style="bold #0088FF")

    def display_history(self) -> None:
        """Display enterprise session history."""
        if not self.chat_history:
            console.print("No enterprise session history yet", style="yellow")
            return
        
        console.print(Panel("Enterprise Session Timeline", border_style="#0088FF", title_style="bold #0088FF"))
        
        for i, entry in enumerate(self.chat_history, 1):
            timestamp = entry['timestamp'].strftime("%H:%M:%S")
            if entry['type'] == 'user':
                console.print(f"{i}. Enterprise User [{timestamp}] {entry['message'][:100]}{'...' if len(entry['message']) > 100 else ''}")
            else:
                console.print(f"{i}. AI Platform [{timestamp}] Generated enterprise infrastructure")
        console.print()

    def display_examples(self) -> None:
        """Display enterprise infrastructure templates."""
        examples_table = Table(title="Enterprise Infrastructure Templates", box=ROUNDED, title_style="bold #0088FF")
        examples_table.add_column("Platform", style="bold #0088FF", width=15)
        examples_table.add_column("Enterprise Template", style="white")
        
        examples = [
            ("AWS Enterprise", "Deploy production AWS 3-tier architecture with high availability and compliance"),
            ("Kubernetes", "Enterprise Kubernetes platform with service mesh, monitoring, and security"),
            ("Docker Enterprise", "Enterprise container orchestration for microservices with monitoring"),
            ("Terraform", "Enterprise-grade Terraform modules for scalable cloud infrastructure"),
            ("Multi-Cloud", "Hybrid enterprise cloud architecture with AWS, Azure, and compliance"),
            ("Serverless", "Enterprise serverless data pipeline with security and monitoring"),
            ("Security", "Enterprise security architecture with zero-trust and compliance monitoring"),
            ("Architecture", "Generate comprehensive architecture diagrams with security documentation")
        ]
        
        for category, example in examples:
            examples_table.add_row(category, example)
        
        console.print(examples_table)

    async def toggle_mode(self) -> None:
        """Toggle between AI chat mode and project generation mode."""
        current_mode = "Project Generation" if self.project_mode else "AI Chat"
        new_mode = "AI Chat" if self.project_mode else "Project Generation"
        
        console.print(f"\n🔄 Current mode: {current_mode}")
        
        if Confirm.ask(f"Switch to {new_mode} mode?", default=True):
            self.project_mode = not self.project_mode
            mode_name = "Project Generation" if self.project_mode else "AI Chat"
            console.print(f"✅ Switched to {mode_name} mode", style="bold green")
            
            if self.project_mode:
                console.print("🚀 In Project Generation mode, describe projects to generate complete applications")
                console.print("Example: 'Create a todo app with React and Node.js backend'")
            else:
                console.print("🤖 In AI Chat mode, ask questions or request individual code snippets")
                console.print("Example: 'Write a Python function to sort a list' or 'Help with Docker setup'")
        else:
            console.print(f"Staying in {current_mode} mode")

    async def exit_chat(self) -> bool:
        """Exit the enterprise platform."""
        console.print()
        goodbye_panel = Panel(
            Text.assemble(
                ("Thank you for using SnapInfra Enterprise Platform\n\n", "bold white"),
                ("Enterprise Infrastructure Generated: ", "white"), (str(len([e for e in self.chat_history if e['type'] == 'ai'])), "bold #0088FF"), (" deployments\n", "white"),
                ("Visit our enterprise portal: https://snapinfra.enterprise", "#0088FF")
            ),
            title="Enterprise Session Complete",
            border_style="#0088FF"
        )
        console.print(Align.center(goodbye_panel))
        return True

    def display_ai_message(self, content: str) -> None:
        """Display AI message in clean chat bubble format."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # AI chat bubble - clean rectangular design
        ai_bubble = Panel(
            Text(content, style="white"),
            title=f"SnapInfra Assistant - {timestamp}",
            title_align="left", 
            border_style="green",
            box=SQUARE,  # No rounded corners
            padding=(0, 1),
            width=80
        )
        
        console.print()
        console.print(ai_bubble)
        console.print()

    def get_user_input(self) -> str:
        """Get user input with clean styling."""
        # Clean input prompt
        user_input = Prompt.ask(
            Text.assemble(("snapinfra", "bold #0088FF"), (" > ", "white")),
            console=console
        ).strip()
        
        return user_input

    async def chat_loop(self) -> None:
        """Main chat interaction loop with clean interface."""
        console.print(Text("Ready to code! Type your message below:\n", style="#0088FF"))
        
        while True:
            try:
                # Get user input with clean input box
                user_input = self.get_user_input()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if await self.handle_special_commands(user_input):
                    continue
                
                # Display user message in chat bubble
                self.display_user_message(user_input)
                
                # Store user message in history
                self.chat_history.append({
                    'type': 'user',
                    'message': user_input,
                    'timestamp': datetime.now()
                })
                
                # Always try to generate a project unless it's clearly just a question
                is_question = any(word in user_input.lower() for word in ['how', 'what', 'why', 'when', 'where', 'help', 'explain', '?'])
                is_too_short = len(user_input.strip().split()) < 2
                
                if not is_question and not is_too_short:
                    console.print(f"\n🚀 Generating project: {user_input}")
                    await self._handle_agentic_project_generation(user_input)
                else:
                    console.print(f"\n🤖 AI is thinking...")
                    await self._handle_ai_chat(user_input)
                
                # This code has been moved to separate methods
                
            except KeyboardInterrupt:
                console.print("\n\nEnterprise session interrupted", style="yellow")
                if Confirm.ask("Exit SnapInfra Enterprise Platform?", default=False):
                    await self.exit_chat()
                    break
                continue
            except EOFError:
                await self.exit_chat()
                break

    async def run(self) -> None:
        """Main entry point for interactive mode."""
        # Display beautiful welcome screen
        display_minimal_welcome()
        
        # FIRST: Setup and validate API keys
        if not await self.setup_configuration():
            console.print("\nPlease add your API keys and restart SnapInfra", style="#0088FF")
            return
        
        # SECOND: Select backend and model (only after API keys are ready)
        if not await self.select_backend_and_model():
            return
        
        # THIRD: Clear screen and show clean chat interface with active session
        console.clear()
        self.display_chat_header()
        
        # Start chat loop
        await self.chat_loop()
    
    async def _handle_ai_chat(self, user_input: str) -> None:
        """Handle regular AI chat without project generation."""
        
        if not self.backend or not self.current_model:
            console.print("❌ AI backend not configured", style="red")
            return
        
        try:
            # Validate and clean user input first
            if not user_input or not isinstance(user_input, str) or not user_input.strip():
                console.print("❌ Please provide a valid message", style="red")
                return
                
            clean_input = user_input.strip()
            
            # Create a simple conversation without reusing previous conversations to avoid issues
            from ..types.models import Message
            system_content = "You are SnapInfra AI, an expert DevOps and infrastructure assistant. Provide helpful, accurate responses for infrastructure, cloud, and development questions. Generate actual code when requested, not templates."
            
            try:
                system_message = Message(role="system", content=system_content)
            except Exception as e:
                console.print(f"Error creating system message: {e}", style="red")
                return
                
            conversation = self.backend.chat(self.current_model, system_message)
            
            # Send message and get response
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("AI is generating response...", total=None)
                response = await conversation.send(clean_input)
            
            if response and response.full_output:
                # Display AI response
                self.display_ai_message(response.full_output)
                
                # Store in history
                self.chat_history.append({
                    'type': 'ai',
                    'response': response,
                    'timestamp': datetime.now()
                })
                
                # Update the conversation reference for future use
                self.conversation = conversation
            else:
                console.print("❌ No response from AI", style="red")
                
        except Exception as e:
            console.print(f"❌ AI chat error: {e}", style="red")
    
    async def _handle_project_generation(self, user_input: str) -> None:
        """Handle comprehensive project generation."""
        try:
            # Extract project name from input
            project_name = self._extract_project_name(user_input)
            project_name = self._sanitize_project_name(project_name)
            
            # Create project plan
            project_plan = await self._create_project_plan(user_input, project_name)
            
            if project_plan:
                # Show the plan
                await self._display_project_plan(project_plan)
                
                # Generate and show architecture diagram
                diagram_data = await self._generate_architecture_diagram(project_plan, user_input)
                
                if diagram_data:
                    architecture_approved = False
                    while not architecture_approved:
                        architecture_approved = await self._show_architecture_preview(diagram_data)
                        if not architecture_approved:
                            # Regenerate the diagram
                            console.print("\n🔄 Regenerating architecture diagram...", style="yellow")
                            new_diagram = await self._generate_architecture_diagram(project_plan, user_input)
                            if new_diagram:
                                diagram_data = new_diagram
                            else:
                                console.print("❌ Failed to regenerate diagram. Proceeding without architecture preview.", style="red")
                                architecture_approved = True
                else:
                    console.print("⚠️ Architecture diagram generation skipped or failed. Proceeding with project generation...", style="yellow")
                
                # Ask for final confirmation
                if Confirm.ask("\n✨ Proceed with comprehensive project generation?", default=True):
                    # Let user choose location
                    output_dir = self._choose_output_location(project_name)
                    
                    # Generate the complete project
                    success = await self._execute_project_generation(project_plan, output_dir)
                    
                    if success:
                        console.print(f"\n🎉 Project generated successfully!", style="bold green")
                        
                        # Show next steps
                        await self._display_next_steps(output_dir, project_plan)
                        
                        # Store in history as a successful project generation
                        self.chat_history.append({
                            'type': 'ai',
                            'response': f"Generated complete project '{project_name}' at {output_dir}",
                            'project_data': {
                                'name': project_name,
                                'path': output_dir,
                                'plan': project_plan
                            },
                            'timestamp': datetime.now()
                        })
                    else:
                        console.print("❌ Project generation failed", style="red")
                else:
                    console.print("🚫 Project generation cancelled", style="yellow")
            else:
                console.print("❌ Failed to create project plan", style="red")
                
        except Exception as e:
            console.print(f"Error in comprehensive generation: {e}", style="red")
            console.print("Please try rephrasing your project description or use /help for assistance", style="#0088FF")
    
    async def _handle_agentic_project_generation(self, user_input: str) -> None:
        """Agentic project generation - creates files one by one automatically."""
        try:
            # Extract project name
            project_name = self._extract_project_name(user_input)
            project_name = self._sanitize_project_name(project_name)
            
            # Create output directory in current working directory
            import os
            current_dir = os.getcwd()
            project_dir = os.path.join(current_dir, project_name)
            
            # Check if directory already exists
            if os.path.exists(project_dir):
                from rich.prompt import Confirm
                if not Confirm.ask(f"Directory '{project_name}' already exists. Overwrite?", default=False):
                    console.print("Project generation cancelled.", style="yellow")
                    return
                import shutil
                shutil.rmtree(project_dir)
            
            # Create project directory
            os.makedirs(project_dir, exist_ok=True)
            console.print(f"\n🏞️ Creating project directory: {project_dir}")
            
            # Use AI to plan and generate files
            await self._agentic_file_generation(user_input, project_name, project_dir)
            
        except Exception as e:
            console.print(f"Error in agentic generation: {e}", style="red")
    
    async def _agentic_file_generation(self, description: str, project_name: str, project_dir: str) -> None:
        """Generate files using multi-agent collaboration approach."""
        if not self.backend:
            console.print("❌ No AI backend available", style="red")
            return
        
        # Try multi-agent approach first if we have Groq
        if hasattr(self.backend, '_api_key') and self.backend._api_key:
            try:
                console.print("🤖 Initializing multi-agent collaboration system...", style="bold blue")
                
                from ..agents import MultiAgentProjectGenerator
                multi_agent = MultiAgentProjectGenerator(
                    backend=self.backend,
                    model=self.current_model,
                    api_key=self.backend._api_key
                )
                
                if await multi_agent.initialize():
                    # Use multi-agent collaborative generation
                    project_result = await multi_agent.generate_project_collaboratively(description, project_name)
                    
                    if project_result and project_result.get('generated_files'):
                        await self._write_multi_agent_files(project_result, project_dir)
                        await multi_agent.cleanup()
                        return
                    else:
                        console.print("⚠️ Multi-agent generation failed, falling back to single agent", style="yellow")
                        await multi_agent.cleanup()
                
            except Exception as e:
                console.print(f"⚠️ Multi-agent system error: {e}, using fallback", style="yellow")
        
        # Fallback to original single-agent approach
        await self._single_agent_file_generation(description, project_name, project_dir)
    
    async def _write_multi_agent_files(self, project_result: dict, project_dir: str) -> None:
        """Write files generated by multi-agent collaboration."""
        generated_files = project_result.get('generated_files', [])
        folders = project_result.get('folder_structure', [])
        
        # Create directory structure
        for folder in folders:
            full_path = os.path.join(project_dir, folder)
            os.makedirs(full_path, exist_ok=True)
        
        # Write generated files
        console.print(f"\n📝 Writing {len(generated_files)} files created by specialized agents...")
        
        for i, file_info in enumerate(generated_files, 1):
            file_path = file_info['path']
            content = file_info.get('content', '')
            generated_by = file_info.get('generated_by', 'agent')
            
            console.print(f"  [{i}/{len(generated_files)}] {file_path} (by {generated_by})")
            
            if content:
                full_file_path = os.path.join(project_dir, file_path)
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                
                try:
                    with open(full_file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    console.print(f"    ✅ {file_path}", style="green")
                except Exception as e:
                    console.print(f"    ❌ Failed to write {file_path}: {e}", style="red")
            else:
                console.print(f"    ⚠️ Skipped {file_path} (no content)", style="yellow")
    
    async def _single_agent_file_generation(self, description: str, project_name: str, project_dir: str) -> None:
        """Fallback single-agent file generation approach."""
        from pathlib import Path
        import os
        import json
        
        console.print("🧠 AI is planning the project structure...")
        
        # Step 1: Get project structure from AI
        structure_prompt = f"""
        You are a senior software architect. Create a comprehensive file structure for this project: "{description}"
        
        Return ONLY a JSON object with this exact format:
        {{
            "project_type": "web_app|api|cli|mobile_app|desktop_app|library",
            "tech_stack": ["main", "technologies", "used"],
            "files": [
                {{
                    "path": "relative/path/to/file.ext",
                    "type": "code|config|docs|test",
                    "description": "Purpose of this file",
                    "priority": 1
                }}
            ]
        }}
        
        Make it a realistic, production-ready project with 8-15 essential files. Include:
        - Main application files
        - Configuration files (package.json, requirements.txt, etc.)
        - README.md
        - Basic folder structure
        - Essential dependency management
        
        Focus on the core essentials, not overwhelming complexity.
        """
        
        try:
            # Get project structure
            conversation = self.backend.chat(self.current_model)
            structure_response = await conversation.send(structure_prompt)
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\{[\s\S]*\}', structure_response.full_output)
            if not json_match:
                console.print("❌ Failed to get valid project structure from AI", style="red")
                return
            
            try:
                project_structure = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                console.print("❌ Failed to parse project structure JSON", style="red")
                return
            
            files_to_create = project_structure.get('files', [])
            if not files_to_create:
                console.print("❌ No files to create in project structure", style="red")
                return
            
            console.print(f"✅ Project structure planned: {len(files_to_create)} files")
            console.print(f"📦 Tech stack: {', '.join(project_structure.get('tech_stack', []))}")
            
            # Step 2: Create directories first
            directories = set()
            for file_info in files_to_create:
                file_path = file_info['path']
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    directories.add(dir_path)
            
            for directory in directories:
                full_dir = os.path.join(project_dir, directory)
                os.makedirs(full_dir, exist_ok=True)
            
            # Step 3: Generate files one by one
            console.print(f"\n📝 Generating {len(files_to_create)} files...")
            
            generated_files = []
            for i, file_info in enumerate(files_to_create, 1):
                file_path = file_info['path']
                file_description = file_info.get('description', 'Project file')
                
                console.print(f"  [{i}/{len(files_to_create)}] {file_path}...")
                
                # Generate content for this specific file
                content = await self._generate_single_file_content(
                    file_info, description, project_name, project_structure, generated_files
                )
                
                if content:
                    # Write the file
                    full_file_path = os.path.join(project_dir, file_path)
                    try:
                        with open(full_file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        generated_files.append(file_info)
                        console.print(f"    ✅ {file_path}", style="green")
                    except Exception as e:
                        console.print(f"    ❌ Failed to write {file_path}: {e}", style="red")
                else:
                    console.print(f"    ⚠️ Skipped {file_path} (no content generated)", style="yellow")
            
            # Step 4: Show completion summary
            console.print(f"\n🎉 Project '{project_name}' generated successfully!")
            console.print(f"📁 Location: {project_dir}")
            console.print(f"📄 Files created: {len(generated_files)}")
            
            # Show next steps based on project type
            await self._show_project_next_steps(project_structure, project_dir)
            
        except Exception as e:
            console.print(f"Error in single-agent file generation: {e}", style="red")
    
    async def _generate_single_file_content(self, file_info: dict, project_description: str, project_name: str, project_structure: dict, generated_files: list) -> str:
        """Generate content for a single file using AI."""
        file_path = file_info['path']
        file_type = file_info.get('type', 'code')
        file_description = file_info.get('description', 'Project file')
        tech_stack = project_structure.get('tech_stack', [])
        
        # Create context about previously generated files
        context_files = []
        for gen_file in generated_files[-3:]:  # Only include last 3 files for context
            context_files.append(f"- {gen_file['path']}: {gen_file.get('description', '')}")
        
        context = "\n".join(context_files) if context_files else "This is the first file being generated."
        
        prompt = f"""
        Generate the complete content for this file in the project "{project_name}":
        
        PROJECT CONTEXT:
        - Description: {project_description}
        - Tech Stack: {', '.join(tech_stack)}
        - Project Type: {project_structure.get('project_type', 'application')}
        
        FILE TO GENERATE:
        - Path: {file_path}
        - Type: {file_type}
        - Purpose: {file_description}
        
        PREVIOUSLY GENERATED FILES:
        {context}
        
        REQUIREMENTS:
        1. Generate ONLY the file content, no explanations or markdown formatting
        2. Make it production-ready and functional
        3. Include proper error handling where applicable
        4. Use best practices for the file type
        5. Make sure it integrates well with the overall project structure
        6. Include appropriate comments but don't over-comment
        7. For config files (package.json, requirements.txt, etc), include realistic dependencies
        8. For README.md, make it comprehensive with setup instructions
        
        Generate the complete file content now:
        """
        
        try:
            conversation = self.backend.chat(self.current_model)
            response = await conversation.send(prompt)
            
            if response and response.full_output:
                # Clean up the response - remove code block markers if present
                content = response.full_output.strip()
                
                # Remove markdown code block formatting
                import re
                code_block_pattern = r'^```[\w]*\n?([\s\S]*?)\n?```$'
                match = re.match(code_block_pattern, content, re.MULTILINE)
                if match:
                    content = match.group(1).strip()
                
                return content
            
        except Exception as e:
            console.print(f"Error generating content for {file_path}: {e}", style="red")
        
        return None
    
    async def _show_project_next_steps(self, project_structure: dict, project_dir: str) -> None:
        """Show next steps based on the project type."""
        import os
        project_type = project_structure.get('project_type', 'application')
        tech_stack = project_structure.get('tech_stack', [])
        
        console.print(f"\n🚀 Next Steps to run your {project_type}:")
        
        steps = []
        steps.append(f"cd {os.path.basename(project_dir)}")
        
        # Add steps based on tech stack
        if 'nodejs' in tech_stack or 'node' in tech_stack or any('npm' in t for t in tech_stack):
            steps.append("npm install")
            steps.append("npm start")
        elif 'python' in tech_stack or any('.py' in f.get('path', '') for f in project_structure.get('files', [])):
            steps.append("pip install -r requirements.txt")
            steps.append("python main.py")
        elif 'java' in tech_stack:
            steps.append("mvn clean install")
            steps.append("mvn spring-boot:run")
        elif 'go' in tech_stack:
            steps.append("go mod tidy")
            steps.append("go run main.go")
        elif 'rust' in tech_stack:
            steps.append("cargo build")
            steps.append("cargo run")
        else:
            steps.append("# Follow instructions in README.md")
        
        for i, step in enumerate(steps, 1):
            console.print(f"  {i}. {step}")
        
        console.print(f"\n📖 Check README.md for detailed setup instructions")
        
        # Offer to open the directory
        from rich.prompt import Confirm
        if Confirm.ask("\n📂 Open project directory?", default=True):
            import subprocess
            import sys
            try:
                if sys.platform == 'win32':
                    subprocess.run(['explorer', project_dir], check=True)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', project_dir], check=True)
                else:
                    subprocess.run(['xdg-open', project_dir], check=True)
                console.print(f"📁 Opened {project_dir}")
            except Exception as e:
                console.print(f"Could not open directory: {e}", style="yellow")
    
    def _clean_ai_response(self, response: str) -> str:
        """Clean AI response text for better JSON extraction."""
        import re
        
        # Remove common AI prefixes
        response = re.sub(r'^\s*Here\'s.*?:\s*', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'^\s*Based on.*?:\s*', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'^\s*I\'ll create.*?:\s*', '', response, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove trailing explanations
        response = re.sub(r'\n\nThis (project|structure|plan).*$', '', response, flags=re.DOTALL | re.IGNORECASE)
        response = re.sub(r'\n\nThe above.*$', '', response, flags=re.DOTALL | re.IGNORECASE)
        
        return response.strip()
    
    def _fix_json_issues(self, json_text: str) -> str:
        """Fix common JSON issues in AI responses."""
        import re
        
        # Remove comments
        json_text = re.sub(r'//.*?(?=\n|$)', '', json_text, flags=re.MULTILINE)
        json_text = re.sub(r'/\*.*?\*/', '', json_text, flags=re.DOTALL)
        
        # Fix trailing commas
        json_text = re.sub(r',\s*([}\]])', r'\1', json_text)
        
        # Fix single quotes to double quotes
        json_text = re.sub(r"(?<!\\)'([^'\n\r]*?)(?<!\\)'", r'"\1"', json_text)
        
        # Fix unquoted keys
        json_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_text)
        
        return json_text
    
    def _validate_ai_project_plan(self, plan: dict) -> bool:
        """Validate that a parsed object is a meaningful project plan."""
        if not isinstance(plan, dict):
            return False
        
        # Must have files array
        if 'files' not in plan or not isinstance(plan['files'], list):
            return False
        
        # Must have at least 3 files for a real project
        if len(plan['files']) < 3:
            return False
        
        # Each file must have a path
        for file_info in plan['files']:
            if not isinstance(file_info, dict) or 'path' not in file_info:
                return False
            if not file_info['path'] or not isinstance(file_info['path'], str):
                return False
        
        # Should have some indication of project type or tech stack
        has_project_indicators = any(key in plan for key in [
            'project_type', 'tech_stack', 'description', 'dependencies'
        ])
        
        return has_project_indicators
    
    async def _final_ai_attempt(self, description: str, project_name: str) -> dict:
        """Final attempt with maximum clarity prompt - no fallbacks allowed."""
        if not self.backend:
            console.print("❌ No AI backend available", style="red")
            raise Exception("Cannot generate project without AI backend")
        
        # Ultra-specific prompt designed to force proper JSON
        final_prompt = f"""
You MUST respond with ONLY valid JSON. No explanations, no markdown, just JSON.

Project: {description}
Name: {project_name}

Your response must be EXACTLY this format:

{{
  "project_type": "web_app",
  "tech_stack": ["React", "Node.js", "Express"],
  "description": "A complete {description}",
  "files": [
    {{"path": "frontend/src/App.js", "type": "frontend", "description": "Main React app", "priority": 1}},
    {{"path": "backend/server.js", "type": "backend", "description": "Express server", "priority": 1}},
    {{"path": "package.json", "type": "config", "description": "Dependencies", "priority": 1}},
    {{"path": "README.md", "type": "docs", "description": "Documentation", "priority": 2}}
  ],
  "folders": ["frontend/src", "backend", "docs"],
  "docker_needed": true,
  "database": "mongodb",
  "api_endpoints": 8,
  "complexity": "medium"
}}

Include 8-20 files based on project complexity. RESPOND WITH ONLY THE JSON OBJECT.
        """
        
        try:
            conversation = self.backend.chat(self.current_model)
            response = await conversation.send(final_prompt.strip())
            
            # Very aggressive final parsing
            raw = response.full_output.strip()
            
            # Remove everything that's not JSON
            import re
            json_match = re.search(r'({.*})', raw, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                fixed = self._fix_json_issues(json_text)
                
                import json
                plan = json.loads(fixed)
                
                if self._validate_ai_project_plan(plan):
                    console.print("✅ Final AI attempt successful!", style="bold green")
                    return plan
            
            console.print("❌ Final AI attempt failed - could not generate valid project plan", style="red")
            raise Exception("AI unable to generate valid project plan after multiple attempts")
            
        except Exception as e:
            console.print(f"❌ Final AI attempt failed: {e}", style="red")
            raise Exception("Pure AI generation failed - no fallback templates available")


async def start_interactive_mode():
    """Start the interactive chat mode."""
    chat = SnapInfraChat()
    await chat.run()


# Alias for backward compatibility
SnapInfraInteractiveCLI = SnapInfraChat
