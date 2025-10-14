"""Main CLI application for KITECH Repository."""

import typer
from rich.console import Console

from kitech_repository import __version__
from kitech_repository.cli.commands import auth, download, explore, list_cmd, manager, upload

console = Console()
app = typer.Typer(
    name="kitech",
    help="KITECH Manufacturing Data Repository CLI",
    add_completion=False,
)

# Global option for server URL
server_option = typer.Option(
    None,
    "--server",
    "-s",
    help="KITECH API server URL (e.g., http://server:6300/v1)",
    envvar="KITECH_API_BASE_URL"
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
    from kitech_repository.core.exceptions import ApiError, AuthenticationError

    try:
        with KitechClient() as client:
            result = client.test_connection()
            user = result.get('user', {})
            console.print("[green]✅ 연결 성공![/green]")
            console.print(f"사용자 이름: {user.get('name', 'N/A')}")
            console.print(f"사용자 이메일: {user.get('email', 'N/A')}")
            console.print(f"메시지: {result.get('message', 'N/A')}")
    except AuthenticationError:
        console.print("[red]❌ 인증 실패. 먼저 로그인하세요:[/red]")
        console.print("  kitech-dev auth login")
    except ApiError as e:
        console.print(f"[red]❌ 연결 실패: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ 예상치 못한 오류: {e}[/red]")


if __name__ == "__main__":
    app()
