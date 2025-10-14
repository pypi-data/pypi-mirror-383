"""List commands for CLI."""

import typer
from rich.console import Console
from rich.table import Table

from kitech_repository.core.client import KitechClient
from kitech_repository.core.exceptions import AuthenticationError

console = Console()
app = typer.Typer()


def format_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


@app.command(name="repos")
def list_repositories(
    page: int = typer.Option(0, "--page", "-p", help="Page number"),
    limit: int = typer.Option(20, "--limit", "-l", help="Items per page"),
    include_shared: bool = typer.Option(True, "--include-shared/--no-shared", help="Include shared repositories"),
):
    """List available repositories."""
    try:
        with KitechClient() as client:
            result = client.list_repositories(page=page, limit=limit, include_shared=include_shared)

            if not result["repositories"]:
                console.print("[yellow]No repositories found[/yellow]")
                return

            table = Table(title="Repositories", header_style="", border_style="")
            table.add_column("이름")
            table.add_column("소유자")
            table.add_column("공개여부")

            for repo in result["repositories"]:
                table.add_row(
                    repo.name,
                    repo.owner_name,
                    "공개" if repo.is_public else "비공개"
                )

            console.print(table)
            console.print(f"\nTotal repositories: {result['total_count']}")
    except AuthenticationError:
        console.print("[red]❌ Authentication required. Please login first with:[/red]")
        console.print("  kitech auth login")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="files")
def list_files(
    repository_id: int = typer.Argument(..., help="Repository ID"),
    prefix: str = typer.Option("", "--prefix", "-p", help="Directory prefix to list"),
    search: str = typer.Option(None, "--search", "-s", help="Search for files matching pattern"),
):
    """List files in a repository."""
    try:
        with KitechClient() as client:
            result = client.list_files(repository_id=repository_id, prefix=prefix, search=search)

            if not result["files"]:
                console.print("[yellow]No files found[/yellow]")
                return

            console.print(f"📁 Repository #{repository_id} files")
            if prefix:
                console.print(f"📂 Path: {prefix}")
            if search:
                console.print(f"🔍 Search: {search}")
            console.print("-" * 60)

            for file in result["files"]:
                if file.is_directory:
                    console.print(f"📁 {file.name}/")
                else:
                    size_str = format_size(file.size)
                    console.print(f"📄 {file.name:<40} {size_str:>15}")

            console.print(f"\nTotal items: {result['total_count']}")
    except AuthenticationError:
        console.print("[red]❌ Authentication required. Please login first with:[/red]")
        console.print("  kitech auth login")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)