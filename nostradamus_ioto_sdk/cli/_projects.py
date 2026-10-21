"""Project CLI commands."""

import json
from typing import Optional

import click
from rich import box
from rich.panel import Panel
from rich.table import Table

from nostradamus_ioto_sdk.cli._shared import (
    api_key_option,
    base_url_option,
    console,
    format_option,
    get_client,
    handle_error,
)


@click.group(name="projects")
def projects() -> None:
    """Manage projects."""


@projects.command(name="list")
@api_key_option
@base_url_option
@format_option
@click.option("--limit", "-n", type=int, help="Limit results")
def projects_list(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    limit: Optional[int],
) -> None:
    """List all projects."""
    try:
        client = get_client(api_key, base_url)
        project_list = client.projects.list()

        if not project_list:
            console.print("[yellow]No projects found.[/yellow]")
            return

        if limit:
            project_list = project_list[:limit]

        if output_format == "json":
            console.print_json(
                json.dumps([p.model_dump() for p in project_list], default=str)
            )
        elif output_format == "compact":
            for p in project_list:
                console.print(f"{p.project_name} ({p.project_id})")
        else:
            table = Table(
                title=f"[bold cyan]Projects[/bold cyan] ({len(project_list)} total)",
                box=box.ROUNDED,
            )
            table.add_column("ID", style="dim", no_wrap=True, width=10)
            table.add_column("Name", style="cyan bold")
            table.add_column("Description", style="white")
            table.add_column("Created", style="yellow", no_wrap=True)

            for p in project_list:
                table.add_row(
                    str(p.project_id)[:8] + "...",
                    p.project_name,
                    (p.description or "-")[:50],
                    p.creation_date.strftime("%Y-%m-%d"),
                )
            console.print(table)
    except Exception as e:
        handle_error(e)


@projects.command(name="get")
@api_key_option
@base_url_option
@format_option
@click.argument("project_id")
def projects_get(
    api_key: Optional[str], base_url: Optional[str], output_format: str, project_id: str
) -> None:
    """Get project details."""
    try:
        client = get_client(api_key, base_url)
        p = client.projects.get(project_id)

        if output_format == "json":
            console.print_json(p.model_dump_json())
        elif output_format == "compact":
            console.print(f"{p.project_name} ({p.project_id})")
        else:
            table = Table(
                title=f"[bold cyan]Project: {p.project_name}[/bold cyan]",
                box=box.ROUNDED,
                show_header=False,
            )
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Value", style="green")
            table.add_row("ID", str(p.project_id))
            table.add_row("Name", p.project_name)
            table.add_row("Description", p.description or "-")
            table.add_row("Created", p.creation_date.strftime("%Y-%m-%d %H:%M:%S"))
            if p.tags:
                table.add_row("Tags", ", ".join(p.tags))
            console.print(table)
    except Exception as e:
        handle_error(e)


@projects.command(name="create")
@api_key_option
@base_url_option
@click.option("--name", "-n", required=True, help="Project name")
@click.option("--description", "-d", help="Description")
@click.option("--tags", "-t", help="Comma-separated tags")
def projects_create(
    api_key: Optional[str],
    base_url: Optional[str],
    name: str,
    description: Optional[str],
    tags: Optional[str],
) -> None:
    """Create new project."""
    try:
        client = get_client(api_key, base_url)
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        p = client.projects.create(name=name, description=description, tags=tag_list)

        console.print(
            Panel(
                f"[green]✓[/green] Project created!\n\n"
                f"[cyan]ID:[/cyan] {p.project_id}\n"
                f"[cyan]Name:[/cyan] {p.project_name}",
                title="Success",
                border_style="green",
            )
        )
    except Exception as e:
        handle_error(e)


@projects.command(name="update")
@api_key_option
@base_url_option
@click.argument("project_id")
@click.option("--description", "-d", help="Description")
@click.option("--tags", "-t", help="Tags")
def projects_update(
    api_key: Optional[str],
    base_url: Optional[str],
    project_id: str,
    description: Optional[str],
    tags: Optional[str],
) -> None:
    """Update project."""
    try:
        if not description and not tags:
            console.print("[yellow]No updates specified.[/yellow]")
            return

        client = get_client(api_key, base_url)
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        p = client.projects.update(
            project_id=project_id, description=description, tags=tag_list
        )

        console.print(f"[green]✓[/green] Updated: {p.project_name}")
    except Exception as e:
        handle_error(e)


@projects.command(name="delete")
@api_key_option
@base_url_option
@click.argument("project_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def projects_delete(
    api_key: Optional[str], base_url: Optional[str], project_id: str, yes: bool
) -> None:
    """Delete project."""
    try:
        if not yes:
            if not click.confirm(f"Delete project {project_id}?"):
                console.print("[yellow]Cancelled.[/yellow]")
                return

        client = get_client(api_key, base_url)
        client.projects.delete(project_id)
        console.print(f"[green]✓[/green] Deleted project {project_id}")
    except Exception as e:
        handle_error(e)
