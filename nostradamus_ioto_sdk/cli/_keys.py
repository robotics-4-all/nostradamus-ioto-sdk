"""Project API key CLI commands."""

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
from nostradamus_ioto_sdk.models.enums import KeyType


@click.group(name="keys")
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
                    k.created_at[:10],
                )
            console.print(table)
    except Exception as e:
        handle_error(e)


@keys.command(name="get")
@api_key_option
@base_url_option
@format_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.argument("api_key_value")
def keys_get(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    project: str,
    api_key_value: str,
) -> None:
    """Get API key details.

    \b
    Arguments:
      API_KEY_VALUE  The API key to look up
    """
    try:
        client = get_client(api_key, base_url)
        k = client.project_keys.get(project_id=project, api_key=api_key_value)

        if output_format == "json":
            console.print_json(k.model_dump_json())
        elif output_format == "compact":
            console.print(f"{k.key_type} ({k.api_key[:16]}...)")
        else:
            table = Table(
                title="[bold cyan]API Key[/bold cyan]",
                box=box.ROUNDED,
                show_header=False,
            )
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Value", style="green")
            table.add_row("Key", k.api_key)
            table.add_row("Type", k.key_type)
            table.add_row("Project ID", str(k.project_id))
            table.add_row("Created", k.created_at)
            console.print(table)
    except Exception as e:
        handle_error(e)


@keys.command(name="regenerate")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.argument("api_key_value")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def keys_regenerate(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    api_key_value: str,
    yes: bool,
) -> None:
    """Regenerate an API key.

    \b
    Arguments:
      API_KEY_VALUE  The API key to regenerate
    """
    try:
        if not yes:
            if not click.confirm("Regenerate API key? The old key will stop working."):
                console.print("[yellow]Cancelled.[/yellow]")
                return

        client = get_client(api_key, base_url)
        new_key = client.project_keys.regenerate(
            project_id=project, api_key=api_key_value
        )

        console.print(
            Panel(
                f"[green]✓[/green] API key regenerated!\n\n"
                f"[cyan]New Key:[/cyan] {new_key.key_value}\n"
                f"[red]⚠ Save securely - won't be shown again![/red]",
                title="Success",
                border_style="green",
            )
        )
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
