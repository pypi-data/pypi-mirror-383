"""CLI commands for vibe-engineering."""
import json
import os
import importlib.metadata

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import time
from dotenv import load_dotenv

from src.db import MongoDBClient, get_documents, insert_document
from src.llm import FireworksClient
from src.schemas import SpecifySchema

# Load environment variables
load_dotenv()

# Get version dynamically
try:
    __version__ = importlib.metadata.version("vibe-engineering")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.11"  # fallback version

app = typer.Typer(
    name="vibe",
    help="🚀 Vibe Engineering - AI-powered specification and memory management CLI",
    add_completion=False,
    rich_markup_mode="rich"
)


@app.command()
def status():
    """🔍 Show system status and configuration."""
    console = Console()
    
    console.print("\n[bold blue]🚀 Vibe Engineering Status[/bold blue]\n")
    
    # System status panel
    status_info = "[green]✅ CLI Active[/green]\n"
    status_info += f"[cyan]Version:[/cyan] {__version__}\n"
    status_info += "[cyan]Environment:[/cyan] Production"
    
    status_panel = Panel(
        status_info,
        title="📊 System Status",
        border_style="blue",
        box=box.ROUNDED
    )
    console.print(status_panel)
    
    # Quick help
    help_text = """[yellow]💡 Quick Commands:[/yellow]
    
• [cyan]vibe team[/cyan]           Show team members
• [cyan]vibe specify[/cyan]        Generate specifications  
• [cyan]vibe status[/cyan]         Show this status
• [cyan]vibe --help[/cyan]         Full command list"""
    
    help_panel = Panel(
        help_text,
        title="🆘 Quick Help",
        border_style="yellow",
        box=box.ROUNDED
    )
    console.print(help_panel)


@app.command()
def version():
    """📦 Show version information."""
    console = Console()
    
    version_text = Text(f"🚀 Vibe Engineering v{__version__}", style="bold blue")
    console.print(Panel(version_text, box=box.DOUBLE))


@app.command()
def team():
    """👥 Display the team members from the database."""
    console = Console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Loading team members...", total=None)
        
        try:
            with MongoDBClient() as db_client:
                documents = get_documents(
                    db_client=db_client,
                    db_name="master",
                    collection_name="team",
                    query={}
                )
                team_members = [doc["name"] for doc in documents]
                progress.update(task, completed=True)

            if not team_members:
                console.print("\n[red]❌ No team members found.[/red]")
                console.print("[yellow]💡 Tip: Check your database connection and team collection[/yellow]")
                return

            # Create a beautiful table
            table = Table(
                title="🚀 Vibe Engineering Team", 
                title_style="bold magenta",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold blue"
            )
            table.add_column("#", style="cyan", justify="center", width=4)
            table.add_column("👤 Name", style="green", justify="left")
            table.add_column("📊 Status", style="bright_blue", justify="center")
            table.add_column("🕒 Last Seen", style="yellow", justify="center")

            # Add team members to the table
            for i, member in enumerate(team_members, 1):
                table.add_row(
                    str(i), 
                    member, 
                    "✨ Active",
                    "Just now"
                )

            # Display the table with some extra styling
            console.print()
            console.print(table)
            
            # Summary panel
            summary = f"[bold green]Total Members:[/bold green] {len(team_members)}\n"
            summary += "[bold blue]All Active:[/bold blue] ✅\n"
            summary += "[bold yellow]Team Health:[/bold yellow] 🟢 Excellent"
            
            summary_panel = Panel(
                summary,
                title="📈 Team Summary",
                border_style="green",
                box=box.ROUNDED
            )
            console.print(summary_panel)
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n[red]❌ Error loading team:[/red] {e}")
            console.print("[yellow]💡 Check your MongoDB connection and configuration[/yellow]")


@app.command()
def specify(prompt: str, db_name: str = "master", collection_name: str = "llm"):
    """Generate a specification schema using LLM and store it in MongoDB."""
    console = Console()

    try:
        # Check environment variables
        if not os.getenv("FIREWORKS_API_KEY"):
            console.print("[red]❌ FIREWORKS_API_KEY environment variable is not set[/red]")
            console.print("\n[yellow]💡 Setup instructions:[/yellow]")
            console.print("1. Get your API key from https://fireworks.ai")
            console.print("2. Set the environment variable:")
            console.print("   [cyan]export FIREWORKS_API_KEY=your_api_key_here[/cyan]")
            console.print("3. Or add it to your .env file:")
            console.print("   [cyan]echo 'FIREWORKS_API_KEY=your_api_key_here' >> .env[/cyan]")
            return

        # Generate schema using LLM
        llm_client = FireworksClient()
        response = llm_client.generate_with_schema(
            prompt=prompt,
            schema=SpecifySchema.model_json_schema(),
            schema_name="SpecifySchema",
        )

        # Parse the JSON response
        doc = json.loads(response)

        # Store in MongoDB
        with MongoDBClient() as db_client:
            inserted_id = insert_document(
                db_client=db_client,
                db_name=db_name,
                collection_name=collection_name,
                document=doc
            )

        console.print(f"[green]✓[/green] Document stored in {db_name}.{collection_name}")
        console.print(f"[dim]Document ID: {inserted_id}[/dim]\n")

        # Create a copy of doc for display, converting ObjectId to string if present
        display_doc = doc.copy()
        if "_id" in display_doc:
            display_doc["_id"] = str(display_doc["_id"])

        # Pretty print the schema with rich
        console.print("[bold cyan]Generated Schema:[/bold cyan]")
        from rich.syntax import Syntax
        json_str = json.dumps(display_doc, indent=2, default=str)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)

    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing JSON response:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    app()
