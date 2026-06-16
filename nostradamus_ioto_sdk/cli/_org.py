"""Organization CLI commands."""

from typing import Optional

import click
from rich import box
from rich.table import Table

from nostradamus_ioto_sdk.cli._shared import (
    api_key_option,
    base_url_option,
    console,
    format_option,
    get_client,
    handle_error,
)


@click.group(name="org")
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
