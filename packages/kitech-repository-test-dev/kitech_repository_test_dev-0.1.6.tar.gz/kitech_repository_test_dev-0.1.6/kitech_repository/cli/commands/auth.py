"""Authentication commands for CLI."""

import typer
from rich.console import Console
from rich.prompt import Prompt

from kitech_repository.core.auth import AuthManager
from kitech_repository.core.client import KitechClient

console = Console(highlight=False)
app = typer.Typer()


@app.command()
def login(
    token: str = typer.Option(None, "--token", "-t", help="API token (will prompt if not provided)"),
    max_retries: int = typer.Option(3, "--retries", help="Maximum number of retry attempts")
):
    """Login to KITECH Repository."""
    attempt = 0
    while attempt < max_retries:
        if not token or attempt > 0:
            if attempt > 0:
                console.print(f"Attempt {attempt + 1}/{max_retries}")
            token = Prompt.ask("Token", password=True)

        if not token.startswith("kt_"):
            console.print("[red]❌ Invalid token format. Token should start with 'kt_'[/red]")
            token = None
            attempt += 1
            continue

        try:
            auth_manager = AuthManager()

            # First save the token temporarily
            auth_manager.login(token=token)

            # Test connection with the saved token
            with KitechClient() as client:
                result = client.test_connection()

            # Update token with user info
            auth_manager.login(
                token=token,
                user_id=result.get('userId'),
                expires_at=result.get('expiresAt')  # If server provides expiry
            )

            console.print("[green]✅ Login successful![/green]")
            console.print(f"User ID: {result.get('userId')}")
            if result.get('expiresAt'):
                console.print(f"Token expires: {result.get('expiresAt')}")
            return
        except Exception as e:
            console.print(f"[red]❌ Login failed: {e}[/red]")
            token = None
            attempt += 1
            if attempt < max_retries:
                console.print("Please try again with a valid token.")

    console.print(f"[red]❌ Login failed after {max_retries} attempts[/red]")
    raise typer.Exit(1)


@app.command()
def logout():
    """Logout from KITECH Repository."""
    try:
        auth_manager = AuthManager()
        if auth_manager.logout():
            console.print("[green]✅ Logged out successfully![/green]")
        else:
            console.print("⚠️ You were not logged in")
    except Exception as e:
        console.print(f"[red]❌ Logout failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Check authentication status."""
    try:
        auth_manager = AuthManager()
        if auth_manager.is_authenticated():
            with KitechClient() as client:
                result = client.test_connection()
                console.print("[green]✅ Authenticated[/green]")
                console.print(f"User ID: {result.get('userId')}")
        else:
            console.print("⚠️ Not authenticated")
            console.print("Run 'kitech auth login' to authenticate")
    except Exception as e:
        console.print(f"[red]❌ Error checking status: {e}[/red]")
        raise typer.Exit(1)