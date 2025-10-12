#!/usr/bin/env python3
"""
Universal AI Memory - CLI
Easy installation and management
"""

import click
import os
import sys
import subprocess
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def main():
    """RAGMax - Advanced RAG memory system for AI platforms"""
    pass

@main.command()
@click.option('--cloud', type=click.Choice(['aws', 'gcp', 'azure', 'local']), default='local', help='Deployment target')
@click.option('--mode', type=click.Choice(['full', 'managed']), default='managed', help='Installation mode')
def setup(cloud, mode):
    """Setup RAGMax"""
    console.print(Panel.fit(
        "[bold cyan]RAGMax Setup[/bold cyan]\n"
        "Advanced RAG memory system for AI platforms",
        border_style="cyan"
    ))
    
    if mode == 'managed':
        setup_managed()
    else:
        setup_full(cloud)

def setup_managed():
    """Setup with managed cloud services (recommended)"""
    console.print("\n[bold green]Managed Setup[/bold green] - Using cloud services\n")
    
    # Get user info
    user_name = Prompt.ask("Enter your name", default="user")
    email = Prompt.ask("Enter your email")
    
    # API keys
    console.print("\n[bold]API Keys Setup[/bold]")
    console.print("Get free keys from:")
    console.print("  • Voyage AI: https://www.voyageai.com/")
    console.print("  • Cohere: https://cohere.com/\n")
    
    voyage_key = Prompt.ask("Voyage AI API key (or press Enter to skip)", default="")
    cohere_key = Prompt.ask("Cohere API key (or press Enter to skip)", default="")
    
    if not voyage_key and not cohere_key:
        console.print("[yellow]⚠️  No API keys provided. You'll need to add them later.[/yellow]")
    
    # Database choice
    console.print("\n[bold]Database Setup[/bold]")
    db_choice = Prompt.ask(
        "Choose database",
        choices=["supabase", "neon", "local"],
        default="supabase"
    )
    
    if db_choice == "local":
        setup_local_databases()
    else:
        setup_cloud_database(db_choice)
    
    # Create config
    config = {
        "user_name": user_name,
        "email": email,
        "voyage_key": voyage_key,
        "cohere_key": cohere_key,
        "database": db_choice,
        "mode": "managed"
    }
    
    save_config(config)
    
    # Install Node.js dependencies
    console.print("\n[bold]Installing dependencies...[/bold]")
    install_dependencies()
    
    # Build project
    console.print("\n[bold]Building project...[/bold]")
    build_project()
    
    # Create MCP configs
    console.print("\n[bold]Creating MCP configurations...[/bold]")
    create_mcp_configs(config)
    
    console.print("\n[bold green]✅ Setup complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Restart your AI platform (Kiro, Claude Desktop, etc.)")
    console.print("  2. Try: 'Remember that I love TypeScript'")
    console.print("\nDocumentation: README.md")

def setup_full(cloud):
    """Setup with full control (advanced)"""
    console.print(f"\n[bold green]Full Setup[/bold green] - Deploying to {cloud}\n")
    
    if cloud == 'local':
        setup_local_full()
    elif cloud == 'aws':
        setup_aws()
    elif cloud == 'gcp':
        setup_gcp()
    elif cloud == 'azure':
        setup_azure()

def setup_local_full():
    """Setup local with Docker"""
    # Check Docker
    if not check_docker():
        console.print("[red]❌ Docker not found. Please install Docker Desktop.[/red]")
        console.print("Download from: https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    console.print("[green]✅ Docker found[/green]")
    
    # Start Docker services
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting Docker services...", total=None)
        subprocess.run(["docker-compose", "up", "-d"], check=True, capture_output=True)
        progress.update(task, completed=True)
    
    console.print("[green]✅ Docker services started[/green]")
    
    # Initialize database
    console.print("Initializing database...")
    import time
    time.sleep(5)  # Wait for PostgreSQL
    
    subprocess.run([
        "docker-compose", "exec", "-T", "postgres",
        "psql", "-U", "postgres", "-d", "ai_memory",
        "-f", "/tmp/schema.sql"
    ], check=True)
    
    console.print("[green]✅ Database initialized[/green]")

def setup_cloud_database(provider):
    """Setup cloud database"""
    console.print(f"\n[bold]Setting up {provider}...[/bold]")
    
    if provider == "supabase":
        console.print("\n1. Go to https://supabase.com/")
        console.print("2. Create a new project")
        console.print("3. Get your connection string\n")
        
        db_url = Prompt.ask("Enter Supabase connection string")
        # Save to config
    
    elif provider == "neon":
        console.print("\n1. Go to https://neon.tech/")
        console.print("2. Create a new project")
        console.print("3. Get your connection string\n")
        
        db_url = Prompt.ask("Enter Neon connection string")

def setup_local_databases():
    """Setup local databases with Docker"""
    if not check_docker():
        console.print("[yellow]⚠️  Docker not found. Will use cloud databases.[/yellow]")
        return False
    
    console.print("Starting local databases...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    return True

def check_docker():
    """Check if Docker is installed"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except:
        return False

def install_dependencies():
    """Install Node.js dependencies"""
    subprocess.run(["npm", "install"], check=True)

def build_project():
    """Build TypeScript project"""
    subprocess.run(["npm", "run", "build"], check=True)

def save_config(config):
    """Save configuration"""
    config_dir = Path.home() / ".universal-memory"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    console.print(f"[green]✅ Config saved to {config_file}[/green]")

def create_mcp_configs(config):
    """Create MCP configuration files"""
    current_dir = Path.cwd()
    
    # Kiro config
    kiro_dir = current_dir / ".kiro" / "settings"
    kiro_dir.mkdir(parents=True, exist_ok=True)
    
    mcp_config = {
        "mcpServers": {
            "universal-memory": {
                "command": "node",
                "args": [str(current_dir / "dist" / "index.js")],
                "env": {
                    "DEFAULT_USER_ID": config["user_name"],
                    "VOYAGE_API_KEY": config.get("voyage_key", ""),
                    "COHERE_API_KEY": config.get("cohere_key", "")
                },
                "disabled": False,
                "autoApprove": ["search_memory", "add_to_memory"]
            }
        }
    }
    
    with open(kiro_dir / "mcp.json", "w") as f:
        json.dump(mcp_config, f, indent=2)
    
    console.print(f"[green]✅ Kiro config created[/green]")

@main.command()
def start():
    """Start the MCP server"""
    console.print("[bold cyan]Starting RAGMax...[/bold cyan]")
    
    # Check if built
    if not Path("dist/index.js").exists():
        console.print("[yellow]Project not built. Building now...[/yellow]")
        build_project()
    
    # Start server
    subprocess.run(["node", "dist/index.js"])

@main.command()
def status():
    """Check system status"""
    console.print(Panel.fit("[bold cyan]System Status[/bold cyan]", border_style="cyan"))
    
    # Check Docker
    if check_docker():
        console.print("[green]✅ Docker: Available[/green]")
        
        # Check containers
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                capture_output=True,
                text=True
            )
            running = result.stdout.strip().split("\n")
            console.print(f"[green]✅ Running services: {len(running)}[/green]")
        except:
            console.print("[yellow]⚠️  Docker services not running[/yellow]")
    else:
        console.print("[yellow]⚠️  Docker: Not available[/yellow]")
    
    # Check build
    if Path("dist/index.js").exists():
        console.print("[green]✅ Project: Built[/green]")
    else:
        console.print("[yellow]⚠️  Project: Not built[/yellow]")
    
    # Check config
    config_file = Path.home() / ".universal-memory" / "config.json"
    if config_file.exists():
        console.print("[green]✅ Config: Found[/green]")
    else:
        console.print("[yellow]⚠️  Config: Not found[/yellow]")

@main.command()
@click.option('--platform', type=click.Choice(['kiro', 'claude', 'chatgpt', 'continue', 'cline']), required=True)
def config(platform):
    """Generate MCP config for a platform"""
    console.print(f"[bold]Generating config for {platform}...[/bold]")
    
    current_dir = Path.cwd()
    
    # Platform-specific paths
    config_paths = {
        "kiro": current_dir / ".kiro" / "settings" / "mcp.json",
        "claude": Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        "chatgpt": Path.home() / "Library" / "Application Support" / "ChatGPT" / "mcp_config.json",
        "continue": Path.home() / ".continue" / "config.json",
        "cline": current_dir / ".vscode" / "settings.json"
    }
    
    config_path = config_paths[platform]
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create config
    mcp_config = {
        "mcpServers": {
            "universal-memory": {
                "command": "node",
                "args": [str(current_dir / "dist" / "index.js")],
                "env": {},
                "disabled": False,
                "autoApprove": ["search_memory", "add_to_memory"]
            }
        }
    }
    
    with open(config_path, "w") as f:
        json.dump(mcp_config, f, indent=2)
    
    console.print(f"[green]✅ Config created: {config_path}[/green]")
    console.print(f"\nRestart {platform} to apply changes")

@main.command()
def cloud():
    """Deploy to cloud"""
    console.print("[bold cyan]Cloud Deployment[/bold cyan]\n")
    
    provider = Prompt.ask(
        "Choose cloud provider",
        choices=["aws", "gcp", "azure"],
        default="aws"
    )
    
    console.print(f"\n[bold]Deploying to {provider.upper()}...[/bold]")
    console.print("[yellow]Cloud deployment coming soon![/yellow]")
    console.print("\nFor now, use managed services:")
    console.print("  • Database: Supabase, Neon, or Railway")
    console.print("  • Redis: Upstash")
    console.print("  • Qdrant: Qdrant Cloud")

if __name__ == "__main__":
    main()
