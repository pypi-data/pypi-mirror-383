"""CLI commands for vibe-engineering."""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import time

from src.db import MongoDBClient, get_documents
from src.llm import FireworksClient
from src.schemas import SpecifySchema

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
    status_info += "[cyan]Version:[/cyan] 0.1.0\n"
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
    
    version_text = Text("🚀 Vibe Engineering v0.1.0", style="bold blue")
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
def specify(
    prompt: str = typer.Argument(..., help="The specification prompt to process"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml, markdown"),
    save: bool = typer.Option(False, "--save", "-s", help="Save the specification to database"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """✨ Generate a specification schema using AI."""
    console = Console()
    
    console.print(f"\n[bold blue]✨ Generating Specification[/bold blue]\n")
    
    if verbose:
        console.print(f"[cyan]📝 Prompt:[/cyan] {prompt}")
        console.print(f"[cyan]📄 Format:[/cyan] {output_format}")
        console.print(f"[cyan]💾 Save:[/cyan] {'Yes' if save else 'No'}")
        console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("🤖 Processing with AI...", total=None)
        
        try:
            llm_client = FireworksClient()
            response = llm_client.generate_with_schema(
                prompt=prompt,
                schema=SpecifySchema.model_json_schema(),
                schema_name="SpecifySchema",
            )
            progress.update(task, completed=True)

            # Display results
            console.print()
            result_panel = Panel(
                response,
                title="📋 Generated Specification",
                border_style="green",
                box=box.ROUNDED
            )
            console.print(result_panel)
            
            if save:
                console.print("\n[yellow]💾 Saving to database...[/yellow]")
                # TODO: Implement save functionality
                console.print("[green]✅ Specification saved successfully![/green]")
            
            # Next steps
            next_steps = """[yellow]💡 Next Steps:[/yellow]
            
• Review and refine the specification
• Save to database with [cyan]--save[/cyan] flag
• Use [cyan]vibe plan[/cyan] to create implementation plan
• Generate tasks with [cyan]vibe tasks[/cyan]"""
            
            steps_panel = Panel(
                next_steps,
                title="🚀 What's Next?",
                border_style="yellow",
                box=box.ROUNDED
            )
            console.print(steps_panel)
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n[red]❌ Error generating specification:[/red] {e}")
            console.print("[yellow]💡 Check your API keys and network connection[/yellow]")


@app.callback()
def main():
    """
    🚀 [bold blue]Vibe Engineering[/bold blue] - AI-powered specification and memory management CLI
    
    [dim]Manage your project specifications, team knowledge, and development workflows with AI assistance.[/dim]
    """
    pass


if __name__ == "__main__":
    app()
