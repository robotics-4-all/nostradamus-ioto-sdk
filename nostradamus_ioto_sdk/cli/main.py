"""Command-line interface for Nostradamus IoT Observatory SDK."""

import click

from nostradamus_ioto_sdk.cli._collections import collections
from nostradamus_ioto_sdk.cli._data import data
from nostradamus_ioto_sdk.cli._keys import keys
from nostradamus_ioto_sdk.cli._org import org
from nostradamus_ioto_sdk.cli._projects import projects
from nostradamus_ioto_sdk.cli._shared import console


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


cli.add_command(org)
cli.add_command(projects)
cli.add_command(collections)
cli.add_command(data)
cli.add_command(keys)


if __name__ == "__main__":
    cli.main(standalone_mode=True)
