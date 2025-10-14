"""
SnapInfra CLI - Diagram Generation Commands

This module adds diagram generation capabilities to the SnapInfra CLI,
allowing users to create architecture diagrams from infrastructure code.
"""

import json
import sys
import os
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add architecture_diagrams to Python path
ARCH_DIAGRAMS_PATH = Path(__file__).parent.parent.parent.parent / "architecture_diagrams"
sys.path.append(str(ARCH_DIAGRAMS_PATH))

from architecture_diagrams.backend.diagram.generator import DiagramGenerator
from architecture_diagrams.shared.types.diagram_models import InfrastructureDiagram

# Import collaboration modules
try:
    from ..diagram.api_server import start_api_server, stop_api_server, APIClient, get_api_server_status
    from ..diagram.version_control import DiagramVersionControl
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False

console = Console()


@click.group(name='diagram')
def diagram_group():
    """Generate and manage architecture diagrams from infrastructure code."""
    pass


@diagram_group.command('generate')
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output file path for the generated diagram'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['json', 'png', 'svg', 'pdf']),
    default='json',
    help='Output format for the diagram'
)
@click.option(
    '--layout', '-l',
    type=click.Choice(['hierarchical', 'force_directed', 'grid', 'circular', 'layered']),
    default='hierarchical',
    help='Layout algorithm to use for positioning nodes'
)
@click.option(
    '--title', '-t',
    help='Custom title for the diagram'
)
@click.option(
    '--web', '-w',
    is_flag=True,
    help='Open the diagram in the web editor after generation'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed information during generation'
)
def generate_diagram(
    input_file: Path,
    output: Optional[Path],
    format: str,
    layout: str,
    title: Optional[str],
    web: bool,
    verbose: bool
):
    """Generate an architecture diagram from infrastructure code.
    
    INPUT_FILE can be a Terraform file (.tf), directory with Terraform files,
    or other supported infrastructure code formats.
    
    Examples:
        snapinfra diagram generate main.tf -o diagram.json
        snapinfra diagram generate ./terraform/ --layout grid --web
        snapinfra diagram generate infra.tf --format png -o architecture.png
    """
    try:
        generator = DiagramGenerator()
        
        # Determine input type
        if input_file.is_file():
            file_type = _detect_file_type(input_file)
            if verbose:
                console.print(f"📄 Detected file type: {file_type}")
        elif input_file.is_dir():
            file_type = 'terraform_directory'
            if verbose:
                console.print(f"📁 Processing directory: {input_file}")
        else:
            console.print("[red]❌ Input must be a file or directory[/red]")
            return
        
        # Generate diagram with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating diagram...", total=None)
            
            # Generate based on file type
            if file_type == 'terraform' or file_type == 'terraform_json':
                diagram = generator.generate_from_terraform(
                    input_file,
                    layout_algorithm=layout,
                    include_metadata=True
                )
            elif file_type == 'terraform_directory':
                diagram = generator.generate_from_terraform_directory(
                    input_file,
                    layout_algorithm=layout,
                    include_metadata=True
                )
            else:
                console.print(f"[red]❌ Unsupported file type: {file_type}[/red]")
                return
            
            # Set custom title if provided
            if title:
                diagram.metadata.title = title
            
            progress.update(task, description="Diagram generated successfully!")
        
        # Display diagram information
        _display_diagram_info(diagram, verbose)
        
        # Output handling
        if format == 'json':
            if output:
                generator.export_to_json(diagram, output)
                console.print(f"[green]✅ Diagram saved to {output}[/green]")
            else:
                # Print to stdout
                diagram_dict = generator.export_to_dict(diagram)
                print(json.dumps(diagram_dict, indent=2))
        
        elif format in ['png', 'svg', 'pdf']:
            if not output:
                output = Path(f"diagram.{format}")
            
            console.print(f"[yellow]📤 Exporting to {format.upper()} format...[/yellow]")
            # Note: This would require the frontend export functionality
            console.print(f"[blue]ℹ️  {format.upper()} export requires the web interface[/blue]")
            console.print(f"[blue]ℹ️  Use --web flag to open in browser for export[/blue]")
        
        # Open in web interface if requested
        if web:
            _open_web_interface(diagram)
            
    except Exception as e:
        console.print(f"[red]❌ Error generating diagram: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@diagram_group.command('serve')
@click.option(
    '--port', '-p',
    type=int,
    default=8000,
    help='Port to run the diagram server on'
)
@click.option(
    '--host',
    default='localhost',
    help='Host to bind the server to'
)
@click.option(
    '--dev',
    is_flag=True,
    help='Run in development mode with auto-reload'
)
def serve_diagram_interface(port: int, host: str, dev: bool):
    """Start the web-based diagram editor interface.
    
    This starts a local server that provides a web interface for
    creating and editing infrastructure diagrams interactively.
    
    Examples:
        snapinfra diagram serve
        snapinfra diagram serve --port 3000 --dev
    """
    try:
        # Import the web server
        from architecture_diagrams.web_server import start_diagram_server
        from architecture_diagrams.shared.types.diagram_models import InfrastructureDiagram
        
        console.print(Panel(
            f"🚀 Starting SnapInfra Diagram Server\n\n"
            f"URL: http://{host}:{port}\n"
            f"Mode: {'Development' if dev else 'Production'}",
            title="Diagram Server",
            border_style="green"
        ))
        
        # Create empty diagram for now
        empty_diagram_data = {
            "id": "empty-diagram",
            "nodes": [],
            "edges": [],
            "metadata": {
                "title": "SnapInfra Diagram Server",
                "description": "Ready to display diagrams. Generate a diagram with --web flag to see it here.",
                "version": "1.0.0",
                "tags": [],
                "source_files": [],
                "auto_layout": True,
                "layout_algorithm": "hierarchical"
            }
        }
        
        # Start the server
        server, url = start_diagram_server(empty_diagram_data, port, open_browser=True)
        
        try:
            console.print(f"[green]✅ Server started at {url}[/green]")
            console.print("[yellow]Press Ctrl+C to stop the server[/yellow]")
            console.print("[blue]Tip: Generate diagrams with 'snapinfra diagram generate file.tf --web'[/blue]")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]🛑 Stopping server...[/yellow]")
            server.shutdown()
            console.print("[green]✅ Server stopped successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error starting server: {str(e)}[/red]")
        sys.exit(1)


@diagram_group.command('list-layouts')
def list_layouts():
    """List all available layout algorithms."""
    layouts = [
        ('hierarchical', 'Hierarchical layout based on dependencies'),
        ('force_directed', 'Force-directed layout using physics simulation'),
        ('grid', 'Simple grid layout'),
        ('circular', 'Circular layout around a center point'),
        ('layered', 'Layered layout grouped by component type'),
    ]
    
    table = Table(title="Available Layout Algorithms")
    table.add_column("Layout", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    
    for layout, description in layouts:
        table.add_row(layout, description)
    
    console.print(table)


@diagram_group.command('validate')
@click.argument('diagram_file', type=click.Path(exists=True, path_type=Path))
def validate_diagram(diagram_file: Path):
    """Validate a diagram file for correctness.
    
    DIAGRAM_FILE should be a JSON file containing diagram data.
    
    Examples:
        snapinfra diagram validate diagram.json
    """
    try:
        with open(diagram_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic validation
        required_fields = ['id', 'nodes', 'edges', 'metadata']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            console.print(f"[red]❌ Missing required fields: {', '.join(missing_fields)}[/red]")
            return
        
        # Validate structure
        nodes = data['nodes']
        edges = data['edges']
        
        node_ids = {node['id'] for node in nodes}
        
        # Check edge references
        invalid_edges = []
        for edge in edges:
            if edge['source'] not in node_ids or edge['target'] not in node_ids:
                invalid_edges.append(edge['id'])
        
        if invalid_edges:
            console.print(f"[red]❌ Invalid edge references: {', '.join(invalid_edges)}[/red]")
            return
        
        # Display validation results
        table = Table(title=f"Diagram Validation: {diagram_file.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Status", "[green]✅ Valid[/green]")
        table.add_row("Nodes", str(len(nodes)))
        table.add_row("Edges", str(len(edges)))
        table.add_row("Title", data['metadata'].get('title', 'Untitled'))
        table.add_row("Version", data['metadata'].get('version', 'Unknown'))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error validating diagram: {str(e)}[/red]")
        sys.exit(1)


# Collaboration Commands

@diagram_group.command('collaborate')
@click.argument('diagram_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--port', '-p',
    type=int,
    default=8000,
    help='Port to run the collaboration server on'
)
def start_collaboration(diagram_file: Path, port: int):
    """Start collaborative editing for a diagram.
    
    This starts an API server with real-time collaboration features
    and opens the diagram in a collaborative web editor.
    
    Examples:
        snapinfra diagram collaborate diagram.json
        snapinfra diagram collaborate infra.json --port 8080
    """
    if not COLLABORATION_AVAILABLE:
        console.print("[red]❌ Collaboration features not available[/red]")
        console.print("[blue]ℹ️  Install collaboration dependencies first[/blue]")
        return
    
    try:
        # Start API server
        console.print("[green]🚀 Starting collaboration server...[/green]")
        success = start_api_server(port)
        
        if not success:
            console.print("[red]❌ Failed to start collaboration server[/red]")
            return
        
        # Upload diagram to server
        console.print("[green]📤 Uploading diagram...[/green]")
        client = APIClient()
        
        with open(diagram_file, 'r') as f:
            diagram_data = json.load(f)
        
        result = client.create_diagram(
            name=diagram_data.get('metadata', {}).get('title', diagram_file.stem),
            description=f"Collaborative editing session for {diagram_file.name}"
        )
        
        diagram_id = result['id']
        console.print(f"[green]✅ Diagram uploaded with ID: {diagram_id}[/green]")
        
        # Display collaboration info
        server_url = client.base_url
        web_url = f"{server_url}/diagrams/{diagram_id}"
        
        table = Table(title="Collaboration Session Started")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Diagram ID", diagram_id)
        table.add_row("Server URL", server_url)
        table.add_row("Web Editor", web_url)
        table.add_row("Status", "[green]Active[/green]")
        
        console.print(table)
        
        console.print("\n[yellow]Share the Diagram ID with collaborators to work together![/yellow]")
        console.print("[yellow]Press Ctrl+C to stop the collaboration server[/yellow]")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]🛑 Stopping collaboration server...[/yellow]")
            stop_api_server()
            console.print("[green]✅ Collaboration session ended[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error starting collaboration: {e}[/red]")
        sys.exit(1)


@diagram_group.command('share')
@click.argument('diagram_id')
@click.option(
    '--permissions',
    type=click.Choice(['read', 'write', 'admin']),
    default='read',
    help='Permissions for shared access'
)
@click.option(
    '--expires',
    help='Expiration time (e.g., "2024-12-31", "7d", "24h")'
)
def share_diagram(diagram_id: str, permissions: str, expires: Optional[str]):
    """Create a shareable link for a diagram.
    
    Examples:
        snapinfra diagram share abc123 --permissions write
        snapinfra diagram share abc123 --expires 7d
    """
    if not COLLABORATION_AVAILABLE:
        console.print("[red]❌ Collaboration features not available[/red]")
        return
    
    try:
        client = APIClient()
        result = client.share_diagram(
            diagram_id=diagram_id,
            permissions=permissions,
            expires_at=expires
        )
        
        table = Table(title="Diagram Shared Successfully")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Share ID", result['share_id'])
        table.add_row("Share URL", result['share_url'])
        table.add_row("Permissions", permissions)
        
        if expires:
            table.add_row("Expires", str(result.get('expires_at', 'Never')))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error sharing diagram: {e}[/red]")
        sys.exit(1)


@diagram_group.command('versions')
@click.argument('diagram_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--limit', '-n',
    type=int,
    default=10,
    help='Number of versions to show'
)
def show_versions(diagram_file: Path, limit: int):
    """Show version history for a diagram.
    
    Examples:
        snapinfra diagram versions diagram.json
        snapinfra diagram versions diagram.json --limit 20
    """
    if not COLLABORATION_AVAILABLE:
        console.print("[red]❌ Version control features not available[/red]")
        return
    
    try:
        # Extract diagram ID from file
        with open(diagram_file, 'r') as f:
            data = json.load(f)
        
        diagram_id = data.get('id')
        if not diagram_id:
            console.print("[red]❌ Diagram file missing ID field[/red]")
            return
        
        version_control = DiagramVersionControl()
        versions = version_control.get_versions(diagram_id)
        
        if not versions:
            console.print("[yellow]📝 No version history found[/yellow]")
            return
        
        # Show recent versions
        recent_versions = versions[-limit:] if len(versions) > limit else versions
        
        table = Table(title=f"Version History: {diagram_file.name}")
        table.add_column("Version", style="cyan")
        table.add_column("User", style="yellow")
        table.add_column("Message", style="white")
        table.add_column("Date", style="green")
        
        for version in reversed(recent_versions):
            table.add_row(
                str(version.version_number),
                version.user_id[:8],
                version.message[:50] + "..." if len(version.message) > 50 else version.message,
                version.timestamp.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print(table)
        
        if len(versions) > limit:
            console.print(f"[blue]ℹ️  Showing {limit} most recent versions out of {len(versions)} total[/blue]")
        
    except Exception as e:
        console.print(f"[red]❌ Error showing versions: {e}[/red]")
        sys.exit(1)


@diagram_group.command('server-status')
def server_status():
    """Check the status of the collaboration server."""
    if not COLLABORATION_AVAILABLE:
        console.print("[red]❌ Collaboration features not available[/red]")
        return
    
    try:
        status = get_api_server_status()
        
        table = Table(title="Collaboration Server Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        status_color = "green" if status['status'] == 'running' else "red"
        table.add_row("Status", f"[{status_color}]{status['status'].title()}[/{status_color}]")
        table.add_row("URL", status['url'])
        
        if status.get('health'):
            table.add_row("Service", status['health']['service'])
        
        if status.get('error'):
            table.add_row("Error", f"[red]{status['error']}[/red]")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error checking server status: {e}[/red]")
        sys.exit(1)


def _detect_file_type(file_path: Path) -> str:
    """Detect the type of infrastructure file."""
    suffix = file_path.suffix.lower()
    
    if suffix == '.tf':
        return 'terraform'
    elif suffix == '.json':
        # Could be Terraform JSON or diagram JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'resource' in data or 'data' in data:
                return 'terraform_json'
            elif 'nodes' in data and 'edges' in data:
                return 'diagram_json'
            else:
                return 'unknown_json'
        except:
            return 'unknown'
    elif suffix in ['.yaml', '.yml']:
        return 'kubernetes'
    else:
        return 'unknown'


def _display_diagram_info(diagram: InfrastructureDiagram, verbose: bool = False):
    """Display information about the generated diagram."""
    table = Table(title="Generated Diagram")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    table.add_row("Title", diagram.metadata.title)
    table.add_row("Nodes", str(len(diagram.nodes)))
    table.add_row("Edges", str(len(diagram.edges)))
    table.add_row("Layout", diagram.metadata.layout_algorithm)
    
    if diagram.metadata.tags:
        table.add_row("Tags", ", ".join(diagram.metadata.tags))
    
    if diagram.metadata.description and verbose:
        table.add_row("Description", diagram.metadata.description[:100] + "..." if len(diagram.metadata.description) > 100 else diagram.metadata.description)
    
    console.print(table)
    
    if verbose and diagram.nodes:
        console.print("\n[bold]Node Details:[/bold]")
        node_table = Table()
        node_table.add_column("Label", style="cyan")
        node_table.add_column("Type", style="yellow")
        node_table.add_column("Position", style="white")
        
        for node in diagram.nodes[:10]:  # Show first 10 nodes
            pos = f"({int(node.position.x)}, {int(node.position.y)})"
            node_table.add_row(node.label, node.type.value, pos)
        
        if len(diagram.nodes) > 10:
            node_table.add_row("...", f"({len(diagram.nodes) - 10} more)", "...")
        
        console.print(node_table)


def _open_web_interface(diagram: InfrastructureDiagram):
    """Open the diagram in the web interface."""
    try:
        # Import the web server
        import sys
        from pathlib import Path
        
        web_server_path = ARCH_DIAGRAMS_PATH / "web_server.py"
        sys.path.append(str(ARCH_DIAGRAMS_PATH))
        
        from architecture_diagrams.web_server import start_diagram_server
        from architecture_diagrams.backend.diagram.generator import DiagramGenerator
        
        # Convert diagram to dict
        generator = DiagramGenerator()
        diagram_data = generator.export_to_dict(diagram)
        
        console.print("[green]🌐 Starting web interface...[/green]")
        
        # Start server and open browser
        server, url = start_diagram_server(diagram_data, port=None, open_browser=True)
        
        try:
            console.print(f"[green]✅ Web interface opened at {url}[/green]")
            console.print("[yellow]Press Ctrl+C to stop the server[/yellow]")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]🛑 Stopping web server...[/yellow]")
            server.shutdown()
            console.print("[green]✅ Web server stopped[/green]")
            
    except ImportError as e:
        console.print(f"[red]❌ Web interface not available: {e}[/red]")
        console.print("[blue]ℹ️  The diagram has been generated and can be exported to JSON[/blue]")
    except Exception as e:
        console.print(f"[red]❌ Error starting web interface: {e}[/red]")
        console.print("[blue]ℹ️  The diagram has been generated and can be exported to JSON[/blue]")


# Integration function for the main CLI
def add_diagram_commands(cli_group):
    """Add diagram commands to the main SnapInfra CLI group."""
    cli_group.add_command(diagram_group)


# Example usage for testing
if __name__ == '__main__':
    # Test the CLI commands
    diagram_group()