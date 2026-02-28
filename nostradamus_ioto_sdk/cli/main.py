"""Command-line interface for Nostradamus IoT Observatory SDK."""

import json
import os
import sys
from typing import Optional

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import (
    AuthenticationError,
    NostradamusError,
    ResourceNotFoundError,
    ValidationError,
)
from nostradamus_ioto_sdk.models.enums import KeyType

console = Console()


def get_client(
    api_key: Optional[str] = None, base_url: Optional[str] = None
) -> NostradamusClient:
    """Get authenticated client instance."""
    key = api_key or os.getenv("NOSTRADAMUS_API_KEY")
    if not key:
        console.print(
            "[red]Error:[/red] No API key provided.\n"
            "Use --api-key option or set NOSTRADAMUS_API_KEY environment variable.",
            style="bold",
        )
        sys.exit(1)

    if base_url:
        return NostradamusClient(api_key=key, base_url=base_url)
    return NostradamusClient(api_key=key)


def handle_error(error: Exception) -> None:
    """Handle and display errors."""
    if isinstance(error, AuthenticationError):
        console.print("[red]Authentication Error:[/red] Invalid API key.", style="bold")
    elif isinstance(error, ResourceNotFoundError):
        console.print(f"[red]Not Found:[/red] {error}", style="bold")
    elif isinstance(error, ValidationError):
        console.print(f"[red]Validation Error:[/red] {error}", style="bold")
    elif isinstance(error, NostradamusError):
        console.print(f"[red]API Error:[/red] {error}", style="bold")
    else:
        console.print(f"[red]Error:[/red] {error}", style="bold")
    sys.exit(1)


# Common options
api_key_option = click.option("--api-key", envvar="NOSTRADAMUS_API_KEY", help="API key")
base_url_option = click.option(
    "--base-url", envvar="NOSTRADAMUS_BASE_URL", help="API base URL"
)
format_option = click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json", "compact"]),
    default="table",
    help="Output format",
)


@click.group()
@click.version_option(package_name="nostradamus-ioto-sdk")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def cli(verbose: bool) -> None:
    """Nostradamus IoT Observatory CLI (nioto).

    \b
    Professional CLI for the Nostradamus IoT Observatory platform.

    \b
    Authentication:
      Set NOSTRADAMUS_API_KEY or use --api-key

    \b
    Examples:
      nioto org get
      nioto projects list
      nioto collections list --project PROJECT_ID
    """
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


# =============================================================================
# ORGANIZATION
# =============================================================================


@cli.group(name="org")
def org() -> None:
    """Manage organization."""


@org.command(name="get")
@api_key_option
@base_url_option
@format_option
def org_get(
    api_key: Optional[str], base_url: Optional[str], output_format: str
) -> None:
    """Get organization information."""
    try:
        client = get_client(api_key, base_url)
        organization = client.organizations.get()

        if output_format == "json":
            console.print_json(organization.model_dump_json())
        elif output_format == "compact":
            console.print(
                f"{organization.organization_name} ({organization.organization_id})"
            )
        else:
            table = Table(
                title="[bold cyan]Organization[/bold cyan]",
                box=box.ROUNDED,
                show_header=False,
            )
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Value", style="green")
            table.add_row("ID", str(organization.organization_id))
            table.add_row("Name", organization.organization_name)
            table.add_row("Description", organization.description)
            table.add_row(
                "Created",
                organization.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            )
            if organization.tags:
                table.add_row("Tags", ", ".join(organization.tags))
            console.print(table)
    except Exception as e:
        handle_error(e)


@org.command(name="update")
@api_key_option
@base_url_option
@click.option("--description", "-d", help="Description")
@click.option("--tags", "-t", help="Comma-separated tags")
def org_update(
    api_key: Optional[str],
    base_url: Optional[str],
    description: Optional[str],
    tags: Optional[str],
) -> None:
    """Update organization."""
    try:
        if not description and not tags:
            console.print("[yellow]No updates specified.[/yellow]")
            return

        client = get_client(api_key, base_url)
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        organization = client.organizations.update(
            description=description, tags=tag_list
        )

        console.print(f"[green]✓[/green] Updated: {organization.organization_name}")
    except Exception as e:
        handle_error(e)


# =============================================================================
# PROJECTS
# =============================================================================


@cli.group(name="projects")
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


# =============================================================================
# COLLECTIONS
# =============================================================================


@cli.group(name="collections")
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


# =============================================================================
# DATA
# =============================================================================


@cli.group(name="data")
def data() -> None:
    """Send and retrieve time-series data."""


@data.command(name="send")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--collection", "-c", required=True, help="Collection ID")
@click.option("--data", "-d", "payload", required=True, help="Data points (JSON array)")
def data_send(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    collection: str,
    payload: str,
) -> None:
    """Send data to collection.

    \b
    Example:
      nioto data send -p PROJECT_ID -c COLLECTION_ID -d '[{"value": 25.5}]'
    """
    try:
        client = get_client(api_key, base_url)
        data_points = json.loads(payload)
        if not isinstance(data_points, list):
            data_points = [data_points]

        client.data.send(project_id=project, collection_id=collection, data=data_points)
        console.print(f"[green]✓[/green] Sent {len(data_points)} data point(s)")
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        handle_error(e)


@data.command(name="get")
@api_key_option
@base_url_option
@format_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--collection", "-c", required=True, help="Collection ID")
@click.option("--limit", "-n", type=int, help="Limit results")
def data_get(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    project: str,
    collection: str,
    limit: Optional[int],
) -> None:
    """Get data from collection."""
    try:
        client = get_client(api_key, base_url)
        result = client.data.get(
            project_id=project, collection_id=collection, limit=limit
        )

        if output_format == "json":
            console.print_json(json.dumps(result, default=str))
        else:
            console.print(f"[cyan]Collection:[/cyan] {collection}")
            console.print(f"[cyan]Records:[/cyan] {len(result)}\n")

            if result:
                display_count = min(10, len(result))
                console.print(f"[dim]Showing first {display_count} records:[/dim]\n")
                console.print_json(json.dumps(result[:display_count], default=str))

                if len(result) > display_count:
                    console.print(
                        f"\n[dim]... and {len(result) - display_count} more[/dim]"
                    )
    except Exception as e:
        handle_error(e)


# =============================================================================
# API KEYS
# =============================================================================


@cli.group(name="keys")
def keys() -> None:
    """Manage project API keys."""


@keys.command(name="list")
@api_key_option
@base_url_option
@format_option
@click.option("--project", "-p", required=True, help="Project ID")
def keys_list(
    api_key: Optional[str], base_url: Optional[str], output_format: str, project: str
) -> None:
    """List project API keys."""
    try:
        client = get_client(api_key, base_url)
        key_list = client.project_keys.list(project_id=project)

        if not key_list:
            console.print("[yellow]No API keys found.[/yellow]")
            return

        if output_format == "json":
            console.print_json(
                json.dumps([k.model_dump() for k in key_list], default=str)
            )
        elif output_format == "compact":
            for k in key_list:
                console.print(f"{k.key_type} ({k.api_key[:16]}...)")
        else:
            table = Table(
                title=f"[bold cyan]API Keys[/bold cyan] ({len(key_list)} total)",
                box=box.ROUNDED,
            )
            table.add_column("Key", style="dim", no_wrap=True, width=20)
            table.add_column("Type", style="cyan bold")
            table.add_column("Created", style="yellow", no_wrap=True)

            for k in key_list:
                table.add_row(
                    k.api_key[:16] + "...",
                    k.key_type,
                    k.created_at.strftime("%Y-%m-%d"),
                )
            console.print(table)
    except Exception as e:
        handle_error(e)


@keys.command(name="create")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option(
    "--type",
    "-t",
    "key_type_name",
    required=True,
    type=click.Choice(["read", "write", "master"]),
    help="Key type",
)
def keys_create(
    api_key: Optional[str], base_url: Optional[str], project: str, key_type_name: str
) -> None:
    """Create project API key.

    \b
    Example:
      nioto keys create -p PROJECT_ID -t read
    """
    try:
        client = get_client(api_key, base_url)
        key_type_enum = KeyType(key_type_name)
        key = client.project_keys.create(project_id=project, key_type=key_type_enum)

        console.print(
            Panel(
                f"[green]✓[/green] API key created!\n\n"
                f"[cyan]Key:[/cyan] {key.api_key}\n"
                f"[cyan]Type:[/cyan] {key.key_type}\n"
                f"[red]⚠ Save securely - won't be shown again![/red]",
                title="Success",
                border_style="green",
            )
        )
    except Exception as e:
        handle_error(e)


@keys.command(name="delete")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.argument("api_key_to_delete")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def keys_delete(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    api_key_to_delete: str,
    yes: bool,
) -> None:
    """Delete API key.

    \b
    Arguments:
      API_KEY_TO_DELETE  The API key string to delete
    """
    try:
        if not yes:
            if not click.confirm("Delete API key?"):
                console.print("[yellow]Cancelled.[/yellow]")
                return

        client = get_client(api_key, base_url)
        client.project_keys.delete(project_id=project, api_key=api_key_to_delete)
        console.print("[green]✓[/green] Deleted API key")
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    cli.main(standalone_mode=True)
