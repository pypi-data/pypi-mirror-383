"""Startup animations and branding for SnapInfra CLI."""

import time
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.columns import Columns
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.box import ROUNDED

console = Console()

def create_ascii_logo() -> Text:
    """Create Windows-compatible ASCII art using basic characters."""
    logo = Text()
    
    # Windows-compatible SNAPINFRA ASCII art
    logo.append(" ███████ ███    ██  █████  ██████  ██ ███    ██ ███████ ██████   █████ \n", style="bold #0088FF")
    logo.append(" ██      ████   ██ ██   ██ ██   ██ ██ ████   ██ ██      ██   ██ ██   ██\n", style="bold #0088FF")
    logo.append(" ███████ ██ ██  ██ ███████ ██████  ██ ██ ██  ██ █████   ██████  ███████\n", style="bold #0088FF")
    logo.append("      ██ ██  ██ ██ ██   ██ ██      ██ ██  ██ ██ ██      ██   ██ ██   ██\n", style="bold #0088FF")
    logo.append(" ███████ ██   ████ ██   ██ ██      ██ ██   ████ ██      ██   ██ ██   ██\n", style="bold #0088FF")
    # No subtext - keep it clean
    logo.append("\n", style="#0088FF")
    
    return logo
def create_gradient_logo() -> Text:
    """Create professional header logo using basic characters."""
    logo_lines = [
        "===============================================================================",
        "                           SNAPINFRA ENTERPRISE PLATFORM                      ", 
        "                     Next-Generation Infrastructure Automation                 ",
        "==============================================================================="
    ]
    
    logo = Text()
    colors = ["bold #0088FF", "bold white", "#0088FF", "bold #0088FF"]
    
    for i, line in enumerate(logo_lines):
        logo.append(line + "\n", style=colors[i % len(colors)])
    
    return logo

def create_simple_logo() -> Text:
    """Create ultra-simple logo for maximum compatibility."""
    logo = Text()
    
    logo.append("\n", style="#0088FF")
    logo.append("\n", style="#0088FF")
    logo.append("                   S N A P I N F R A   E N T E R P R I S E\n", style="bold #0088FF")
    logo.append("                 AI Infrastructure Automation Platform\n", style="#0088FF")
    logo.append("\n", style="#0088FF")
    
    return logo

def display_loading_animation() -> None:
    """Display a professional loading animation."""
    with Progress(
        TextColumn("[bold #0088FF]Initializing SnapInfra Enterprise Platform..."),
        BarColumn(bar_width=40, style="#0088FF", complete_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("Starting...", total=100)
        
        steps = [
            ("Loading enterprise configuration...", 20),
            ("Initializing AI infrastructure engines...", 40), 
            ("Establishing secure interactive session...", 70),
            ("Platform ready for infrastructure deployment", 100)
        ]
        
        for step_text, target in steps:
            progress.update(task, description=f"[bold #0088FF]{step_text}")
            while progress.tasks[0].completed < target:
                progress.update(task, advance=2)
                time.sleep(0.05)

def display_feature_showcase() -> None:
    """Display enterprise features in professional layout."""
    features_table = Table(title="Enterprise Platform Capabilities", box=ROUNDED, show_header=False, title_style="bold #0088FF")
    features_table.add_column("", style="bold #0088FF", width=25)
    features_table.add_column("", style="white", width=55)
    
    features = [
        ("AI-Powered Generation", "Enterprise-grade infrastructure provisioning with advanced LLM models"),
        ("Architecture Visualization", "Automated architecture diagrams with compliance documentation"),
        ("High-Performance Inference", "Sub-second infrastructure generation with optimized AI backends"),
        ("Security & Compliance", "Built-in enterprise security policies and regulatory compliance"),
        ("Multi-Cloud Excellence", "Unified provisioning across AWS, Azure, GCP, and hybrid environments"),
        ("Interactive Development", "Conversational infrastructure design with expert AI assistance"),
        ("Enterprise Integration", "Seamless export to CI/CD pipelines and infrastructure repositories"),
        ("Real-Time Collaboration", "Live infrastructure editing with team collaboration features")
    ]
    
    for icon_text, description in features:
        features_table.add_row(icon_text, description)
    
    console.print(features_table)

def display_supported_platforms() -> None:
    """Display enterprise platform support matrix."""
    platforms = [
        ["Infrastructure Engines", "Terraform Enterprise", "AWS CloudFormation", "Azure ARM Templates", "Pulumi Cloud"],
        ["Container Orchestration", "Kubernetes Enterprise", "Docker Enterprise", "Helm Enterprise", "OpenShift"],
        ["Cloud Platforms", "AWS Enterprise", "Azure Enterprise", "Google Cloud Enterprise", "Hybrid Multi-Cloud"],
        ["AI Infrastructure", "Groq Enterprise", "OpenAI Enterprise", "AWS Bedrock", "Azure OpenAI"]
    ]
    
    columns = []
    for platform_group in platforms:
        panel_content = "\n".join([
            f"[bold #0088FF]{platform_group[0]}[/bold #0088FF]",
            ""
        ] + [f"▸ {item}" for item in platform_group[1:]])
        
        panel = Panel(
            panel_content,
            border_style="#0088FF",
            padding=(1, 1),
            width=25
        )
        columns.append(panel)
    
    console.print(Columns(columns, equal=True, expand=True))

def display_welcome_screen() -> None:
    """Display the complete welcome screen."""
    console.clear()
    
    # Logo
    logo = create_gradient_logo()
    console.print(Align.center(logo))
    console.print()
    
    # Enterprise tagline
    tagline = Panel(
        Text.assemble(
            ("Enterprise Infrastructure Automation Platform", "bold white"),
            ("\n", "white"),
            ("AI-Powered Infrastructure • Enterprise Security • Multi-Cloud Excellence", "#0088FF")
        ),
        border_style="#0088FF",
        padding=(1, 2)
    )
    console.print(Align.center(tagline))
    console.print()

def display_quick_start() -> None:
    """Display enterprise quick start guide."""
    quick_start = Table(title="Enterprise Quick Start Guide", box=ROUNDED, show_header=False, title_style="bold #0088FF")
    quick_start.add_column("Command", style="bold #0088FF", width=35)
    quick_start.add_column("Enterprise Use Case", style="white", width=55)
    
    commands = [
        ("snapinfra", "Launch enterprise interactive infrastructure console"),
        ("snapinfra --interactive", "Enter guided infrastructure development mode"),
        ('snapinfra "deploy production VPC"', "Direct enterprise infrastructure provisioning"),
        ("snapinfra -b groq \"k8s cluster\"", "Deploy with high-performance AI backend"),
        ("/help", "Access comprehensive enterprise documentation"),
        ("/examples", "Browse enterprise infrastructure templates")
    ]
    
    for cmd, desc in commands:
        quick_start.add_row(cmd, desc)
    
    console.print(quick_start)

def display_startup_sequence() -> None:
    """Display complete startup sequence."""
    # Welcome screen
    display_welcome_screen()
    
    # Loading animation (optional - can be disabled for faster startup)
    # display_loading_animation() 
    
    # Feature showcase
    display_feature_showcase()
    console.print()
    
    # Supported platforms
    display_supported_platforms()
    console.print()
    
    # Quick start
    display_quick_start()
    console.print()

def display_minimal_welcome() -> None:
    """Display developer-friendly welcome screen."""
    console.clear()
    
    # Show left-aligned ASCII logo
    logo = create_ascii_logo()
    console.print(logo)  # Left-aligned, no centering
    
    # Developer-friendly info panel
    info_panel = Panel(
        Text.assemble(
            ("Interactive Infrastructure Console\n", "bold #0088FF"),
            ("Describe what you want to build and I'll generate the code:\n", "white"),
            ("▸ ", "#0088FF"), ("/help", "bold #0088FF"), (" - Show available commands and usage examples\n", "white"),
            ("▸ ", "#0088FF"), ("/examples", "bold #0088FF"), (" - Browse infrastructure code templates\n", "white"),
            ("▸ ", "#0088FF"), ("/exit", "bold #0088FF"), (" - Exit SnapInfra", "white")
        ),
        title="Ready to Code",
        border_style="#0088FF",
        padding=(1, 2)
    )
    console.print(info_panel)
    console.print()
