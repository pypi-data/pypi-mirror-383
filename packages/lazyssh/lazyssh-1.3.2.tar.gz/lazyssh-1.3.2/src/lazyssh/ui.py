"""UI utilities for LazySSH"""

from pathlib import Path

from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from . import __version__
from .models import SSHConnection

console = Console()


def display_banner() -> None:
    """Display the LazySSH banner with sophisticated styling"""
    # Create ASCII art for the logo
    ascii_art = [
        "██╗      █████╗ ███████╗██╗   ██╗███████╗███████╗██╗  ██╗",
        "██║     ██╔══██╗╚══███╔╝╚██╗ ██╔╝██╔════╝██╔════╝██║  ██║",
        "██║     ███████║  ███╔╝  ╚████╔╝ ███████╗███████╗███████║",
        "██║     ██╔══██║ ███╔╝    ╚██╔╝  ╚════██║╚════██║██╔══██║",
        "███████╗██║  ██║███████╗   ██║   ███████║███████║██║  ██║",
        "╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝",
    ]

    # Build the content using a table for better alignment
    content = Table.grid(padding=0)
    content.add_column(justify="center")

    # Add the ASCII art logo as centered rows
    for line in ascii_art:
        content.add_row(Text(line, style="bright_cyan"))

    # Add tagline
    content.add_row("")
    content.add_row(Text("⚡ Modern SSH Connection Manager ⚡", style="bold magenta"))
    content.add_row("")

    # Add version using the dynamic version from __init__.py
    content.add_row(Text(f"v{__version__}", style="dim blue"))

    # Create panel
    panel = Panel(
        content,
        title="[bold blue]Welcome to LazySSH[/bold blue]",
        subtitle="[dim blue]SSH Made Easy[/dim blue]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2),
    )

    # Print the panel centered
    console.print(Align.center(panel))


def display_menu(options: dict[str, str]) -> None:
    table = Table(show_header=False, border_style="blue")
    table.add_column(justify="center")
    table.add_column(justify="center")
    for key, value in options.items():
        table.add_row(f"[cyan]{key}[/cyan]", f"[white]{value}[/white]")
    console.print(table)


def get_user_input(prompt_text: str) -> str:
    result: str = Prompt.ask(f"[cyan]{prompt_text}[/cyan]")
    return result


def display_error(message: str) -> None:
    console.print(f"[red]Error:[/red] {message}")


def display_success(message: str) -> None:
    console.print(f"[green]Success:[/green] {message}")


def display_info(message: str) -> None:
    console.print(f"{message}")


def display_warning(message: str) -> None:
    console.print(f"[yellow]Warning:[/yellow] {message}")


def display_ssh_status(connections: dict[str, SSHConnection]) -> None:
    table = Table(title="Active SSH Connections", border_style="blue")
    table.add_column("Name", style="cyan", justify="center")
    table.add_column("Host", style="magenta", justify="center")
    table.add_column("Username", style="green", justify="center")
    table.add_column("Port", style="yellow", justify="center")
    table.add_column("Dynamic Port", style="blue", justify="center")
    table.add_column("Active Tunnels", style="red", justify="center")
    table.add_column("Socket Path", style="dim", justify="center")

    for socket_path, conn in connections.items():
        if isinstance(conn, SSHConnection):
            name = Path(socket_path).name
            table.add_row(
                name,
                conn.host,
                conn.username,
                str(conn.port),
                str(conn.dynamic_port or "N/A"),
                str(len(conn.tunnels)),
                socket_path,
            )

    console.print(table)


def display_tunnels(socket_path: str, conn: SSHConnection) -> None:
    if not conn.tunnels:
        display_info("No tunnels for this connection")
        return

    table = Table(title=f"Tunnels for {conn.host}", border_style="blue")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Connection", style="blue", justify="center")
    table.add_column("Type", style="magenta", justify="center")
    table.add_column("Local Port", style="green", justify="center")
    table.add_column("Remote", style="yellow", justify="center")

    for tunnel in conn.tunnels:
        table.add_row(
            tunnel.id,
            tunnel.connection_name,
            tunnel.type,
            str(tunnel.local_port),
            f"{tunnel.remote_host}:{tunnel.remote_port}",
        )

    console.print(table)
