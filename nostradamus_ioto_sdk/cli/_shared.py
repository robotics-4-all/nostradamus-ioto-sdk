"""Shared utilities and common options for the Nostradamus IoT Observatory CLI."""

import os
import sys
from typing import Optional

import click
from rich.console import Console

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import (
    AuthenticationError,
    NostradamusError,
    ResourceNotFoundError,
    ValidationError,
)

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
