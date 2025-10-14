"""
ATAMS CLI - Main entry point
"""
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="atams",
    help="Advanced Toolkit for Application Management System",
    add_completion=False,
)

console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """ATAMS - Advanced Toolkit for Application Management System"""
    if version:
        from atams import __version__
        console.print(f"ATAMS version: {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold cyan]ATAMS[/bold cyan] - Advanced Toolkit for Application Management System\n\n"
            "Available commands:\n"
            "  [green]init[/green]      Initialize new AURA project\n"
            "  [green]generate[/green]  Generate CRUD boilerplate\n\n"
            "Use [yellow]atams --help[/yellow] for more information",
            title="🚀 ATAMS Toolkit",
            border_style="cyan"
        ))


# Import subcommands
from atams.cli.commands import init_cmd, generate

app.command(name="init")(init_cmd.init_project)
app.command(name="generate")(generate.generate_resource)


if __name__ == "__main__":
    app()
