"""
common/console.py

Single shared logging surface for both terminals (ingestion + DQ worker),
so the color scheme is consistent and the demo-recording handoff (yellow in
Terminal 1 -> cyan panel in Terminal 2) reads clearly on screen.

Console-only. Never write ANSI codes into SQLite remarks columns — those
stay plain text so they're clean to query later.
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def log_success(message: str) -> None:
    console.print(f"[bold green]\u2713[/bold green] {message}")


def log_info(message: str) -> None:
    console.print(f"[cyan]\u2139[/cyan] {message}")


def log_warning(message: str) -> None:
    """DQ failures / schema drift use this — yellow, per the demo-recording requirement."""
    console.print(f"[bold yellow]\u26a0 {message}[/bold yellow]")


def log_error(message: str) -> None:
    console.print(f"[bold red]\u2717 {message}[/bold red]")


def log_ai_investigation_started(execution_id: str, dataset: str) -> None:
    """
    Boxed cyan panel — the visible reaction in Terminal 2 the instant an
    alert arrives, before any actual reasoning happens. This is what makes
    the yellow -> cyan causality obvious on a screen recording.
    """
    panel = Panel(
        f"[bold cyan]execution_id:[/bold cyan] {execution_id}\n"
        f"[bold cyan]dataset:[/bold cyan] {dataset}",
        title="[bold cyan]\U0001f50d AI INVESTIGATION STARTED[/bold cyan]",
        border_style="cyan",
    )
    console.print(panel)


def log_run_summary(execution_id: str, dataset: str, file_path: str,
                     row_count: int, injection_summary: str = None) -> None:
    lines = [
        f"[bold]execution_id:[/bold] {execution_id}",
        f"[bold]dataset:[/bold] {dataset}",
        f"[bold]file_path:[/bold] {file_path}",
        f"[bold]row_count:[/bold] {row_count}",
    ]
    if injection_summary:
        lines.append(f"[bold]injection:[/bold] {injection_summary}")
    panel = Panel("\n".join(lines), title="[bold green]Ingestion Complete[/bold green]",
                  border_style="green")
    console.print(panel)