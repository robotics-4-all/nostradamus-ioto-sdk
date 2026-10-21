"""Collection CLI commands."""

import json
import sys
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


@click.group(name="collections")
def collections() -> None:
    """Manage data collections."""


@collections.command(name="list")
@api_key_option
@base_url_option
@format_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--limit", "-n", type=int, help="Limit results")
def collections_list(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    project: str,
    limit: Optional[int],
) -> None:
    """List collections in project."""
    try:
        client = get_client(api_key, base_url)
        coll_list = client.collections.list(project_id=project)

        if not coll_list:
            console.print("[yellow]No collections found.[/yellow]")
            return

        if limit:
            coll_list = coll_list[:limit]

        if output_format == "json":
            console.print_json(
                json.dumps([c.model_dump() for c in coll_list], default=str)
            )
        elif output_format == "compact":
            for c in coll_list:
                console.print(f"{c.collection_name} ({c.collection_id})")
        else:
            table = Table(
                title=f"[bold cyan]Collections[/bold cyan] ({len(coll_list)} total)",
                box=box.ROUNDED,
            )
            table.add_column("ID", style="dim", no_wrap=True, width=10)
            table.add_column("Name", style="cyan bold")
            table.add_column("Description", style="white")
            table.add_column("Project", style="magenta")
            table.add_column("Created", style="yellow", no_wrap=True)

            for c in coll_list:
                table.add_row(
                    str(c.collection_id)[:8] + "...",
                    c.collection_name,
                    (c.description or "-")[:40],
                    c.project_name,
                    c.creation_date.strftime("%Y-%m-%d"),
                )
            console.print(table)
    except Exception as e:
        handle_error(e)


@collections.command(name="get")
@api_key_option
@base_url_option
@format_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.argument("collection_id")
def collections_get(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    project: str,
    collection_id: str,
) -> None:
    """Get collection details."""
    try:
        client = get_client(api_key, base_url)
        c = client.collections.get(project_id=project, collection_id=collection_id)

        if output_format == "json":
            console.print_json(c.model_dump_json())
        elif output_format == "compact":
            console.print(f"{c.collection_name} ({c.collection_id})")
        else:
            table = Table(
                title=f"[bold cyan]Collection: {c.collection_name}[/bold cyan]",
                box=box.ROUNDED,
                show_header=False,
            )
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Value", style="green")
            table.add_row("ID", str(c.collection_id))
            table.add_row("Name", c.collection_name)
            table.add_row("Description", c.description or "-")
            table.add_row("Project", c.project_name)
            table.add_row("Project ID", str(c.project_id))
            table.add_row("Created", c.creation_date.strftime("%Y-%m-%d %H:%M:%S"))
            if c.tags:
                table.add_row("Tags", ", ".join(c.tags))
            console.print(table)
    except Exception as e:
        handle_error(e)


@collections.command(name="create")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--name", "-n", required=True, help="Collection name")
@click.option("--description", "-d", required=True, help="Description")
@click.option("--schema", "-s", required=True, help="Schema (JSON)")
@click.option("--tags", "-t", help="Tags")
def collections_create(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    name: str,
    description: str,
    schema: str,
    tags: Optional[str],
) -> None:
    """Create collection.

    \b
    Example:
      nioto collections create -p PROJECT_ID -n "Sensors" \\
        -d "Temperature data" -s '{"type": "timeseries"}'
    """
    try:
        client = get_client(api_key, base_url)
        schema_dict = json.loads(schema)
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        c = client.collections.create(
            project_id=project,
            name=name,
            description=description,
            collection_schema=schema_dict,
            tags=tag_list,
        )

        console.print(
            Panel(
                f"[green]✓[/green] Collection created!\n\n"
                f"[cyan]ID:[/cyan] {c.collection_id}\n"
                f"[cyan]Name:[/cyan] {c.collection_name}",
                title="Success",
                border_style="green",
            )
        )
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON schema:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        handle_error(e)


@collections.command(name="update")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.argument("collection_id")
@click.option("--description", "-d", help="Description")
@click.option("--tags", "-t", help="Comma-separated tags")
def collections_update(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    collection_id: str,
    description: Optional[str],
    tags: Optional[str],
) -> None:
    """Update collection."""
    try:
        if not description and not tags:
            console.print("[yellow]No updates specified.[/yellow]")
            return

        client = get_client(api_key, base_url)
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        c = client.collections.update(
            project_id=project,
            collection_id=collection_id,
            description=description,
            tags=tag_list,
        )

        console.print(f"[green]✓[/green] Updated: {c.collection_name}")
    except Exception as e:
        handle_error(e)


@collections.command(name="delete")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.argument("collection_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def collections_delete(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    collection_id: str,
    yes: bool,
) -> None:
    """Delete collection."""
    try:
        if not yes:
            if not click.confirm(f"Delete collection {collection_id}?"):
                console.print("[yellow]Cancelled.[/yellow]")
                return

        client = get_client(api_key, base_url)
        client.collections.delete(project_id=project, collection_id=collection_id)
        console.print(f"[green]✓[/green] Deleted collection {collection_id}")
    except Exception as e:
        handle_error(e)
