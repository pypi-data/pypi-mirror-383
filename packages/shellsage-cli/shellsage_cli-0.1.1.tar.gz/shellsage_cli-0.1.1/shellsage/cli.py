import click
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.command()
@click.argument("command", nargs=-1)
def main(command):
    """ShellSage — run any shell command intelligently."""
    cmd = " ".join(command)
    console.print(Panel(f"Running: [bold green]{cmd}[/bold green]"))
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] {e.stderr}")

