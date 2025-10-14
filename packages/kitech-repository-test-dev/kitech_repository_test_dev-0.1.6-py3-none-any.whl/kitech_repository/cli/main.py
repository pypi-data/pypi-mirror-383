"""Main CLI application for KITECH Repository."""

import typer
from rich.console import Console
from rich.table import Table

from kitech_repository import __version__
from kitech_repository.cli.commands import auth, download, list_cmd, upload, explore, manager

console = Console()
app = typer.Typer(
    name="kitech",
    help="KITECH Manufacturing Data Repository CLI",
    add_completion=False,
)

app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(list_cmd.app, name="list", help="List repositories and files")
app.add_typer(download.app, name="download", help="Download files and repositories")
app.add_typer(upload.app, name="upload", help="Upload files to repositories")
app.add_typer(explore.app, name="explore", help="Interactive repository exploration")
app.add_typer(manager.app, name="manager", help="Dual-panel file manager")


@app.command()
def version():
    """Show version information."""
    console.print(f"[bold blue]KITECH Repository CLI[/bold blue] v{__version__}")


@app.command()
def test():
    """Test connection to KITECH API."""
    from kitech_repository.core.client import KitechClient
    from kitech_repository.core.exceptions import AuthenticationError, ApiError

    try:
        with KitechClient() as client:
            result = client.test_connection()
            console.print("[green]✅ Connection successful![/green]")
            console.print(f"User ID: {result.get('userId')}")
            console.print(f"Message: {result.get('message')}")
    except AuthenticationError:
        console.print("[red]❌ Authentication failed. Please login first with:[/red]")
        console.print("  kitech auth login")
    except ApiError as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")


if __name__ == "__main__":
    app()