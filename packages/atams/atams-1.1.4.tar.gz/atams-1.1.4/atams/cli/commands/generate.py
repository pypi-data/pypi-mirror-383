"""
ATAMS Generate Command
Generate full CRUD boilerplate for a resource
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from jinja2 import Environment, PackageLoader, select_autoescape

from atams.utils import ResourceNaming, write_file, auto_register_router

console = Console()


def generate_resource(
    resource_name: str = typer.Argument(..., help="Resource name (singular, e.g., 'department')"),
    schema: str = typer.Option("aura", "--schema", "-s", help="Database schema name"),
    skip_api_register: bool = typer.Option(False, "--skip-api", help="Skip auto-registration to api.py"),
):
    """
    Generate full CRUD boilerplate for a resource

    Example:
        atams generate department
        atams generate user_profile --schema myapp
    """
    console.print(f"\n[bold cyan]🚀 Generating CRUD for:[/bold cyan] {resource_name}")

    # Get naming conventions
    naming = ResourceNaming(resource_name)

    # Display naming info
    console.print(f"[dim]Singular:[/dim] {naming.singular}")
    console.print(f"[dim]Plural:[/dim] {naming.plural}")
    console.print(f"[dim]PascalCase:[/dim] {naming.pascal}")
    console.print(f"[dim]Prefix:[/dim] {naming.prefix}")
    console.print()

    # Setup Jinja2 environment
    try:
        env = Environment(
            loader=PackageLoader('atams', 'cli/templates'),
            autoescape=select_autoescape()
        )
    except Exception as e:
        console.print(f"[red]❌ Error loading templates: {e}[/red]")
        raise typer.Exit(1)

    # Template context
    context = {
        'singular_name': naming.singular,
        'plural_name': naming.plural,
        'pascal_name': naming.pascal,
        'pascal_plural': naming.pascal_plural,
        'table_name': naming.singular,
        'prefix': naming.prefix,
        'db_schema': schema,
    }

    # Detect project root (current directory should have app/ folder)
    cwd = Path.cwd()
    app_dir = cwd / "app"

    if not app_dir.exists():
        console.print("[red]❌ Error: Not in a valid AURA project directory[/red]")
        console.print("[yellow]💡 Hint: Run this command from the project root (where app/ folder is)[/yellow]")
        raise typer.Exit(1)

    files_to_create = [
        ("model.jinja2", app_dir / "models" / naming.model_file, "Model"),
        ("schema.jinja2", app_dir / "schemas" / naming.schema_file, "Schema"),
        ("repository.jinja2", app_dir / "repositories" / naming.repository_file, "Repository"),
        ("service.jinja2", app_dir / "services" / naming.service_file, "Service"),
        ("endpoint.jinja2", app_dir / "api" / "v1" / "endpoints" / naming.endpoint_file, "Endpoint"),
    ]

    created_files = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for template_name, file_path, description in files_to_create:
            task = progress.add_task(f"Creating {description}...", total=None)

            try:
                # Load template
                template = env.get_template(template_name)

                # Render content
                content = template.render(**context)

                # Write file
                write_file(file_path, content)

                created_files.append((file_path, description))
                progress.update(task, completed=True)

            except Exception as e:
                console.print(f"[red]❌ Error creating {description}: {e}[/red]")
                raise typer.Exit(1)

    # Auto-register to api.py
    if not skip_api_register:
        api_file = app_dir / "api" / "v1" / "api.py"

        if api_file.exists():
            console.print()
            console.print("[cyan]📝 Registering router to api.py...[/cyan]")

            try:
                success = auto_register_router(
                    api_file,
                    naming.plural,  # endpoint module name
                    f"/{naming.plural}",  # router prefix
                    naming.pascal_plural  # tags
                )

                if success:
                    console.print("[green]✅ Router registered successfully[/green]")
                else:
                    console.print("[yellow]⚠️  Could not auto-register router (may need manual registration)[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Auto-registration failed: {e}[/yellow]")
                console.print("[yellow]💡 You may need to manually add the router to api.py[/yellow]")
        else:
            console.print(f"[yellow]⚠️  api.py not found at {api_file}[/yellow]")

    # Success summary
    console.print()
    console.print("[bold green]🎉 CRUD generation completed![/bold green]")
    console.print()
    console.print("[bold]Files created:[/bold]")

    for file_path, description in created_files:
        relative_path = file_path.relative_to(cwd)
        console.print(f"  [green]✅[/green] {relative_path} ({description})")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. Create database table: [cyan]CREATE TABLE {schema}.{naming.singular} (...)[/cyan]")
    console.print(f"  2. Customize repository queries if needed")
    console.print(f"  3. Customize service business logic if needed")
    console.print(f"  4. Test endpoints: [cyan]GET /api/v1/{naming.plural}[/cyan]")
    console.print()
