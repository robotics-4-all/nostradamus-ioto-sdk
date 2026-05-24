"""Data CLI commands."""

import json
import sys
from typing import Optional

import click

from nostradamus_ioto_sdk.cli._shared import (
    api_key_option,
    base_url_option,
    console,
    format_option,
    get_client,
    handle_error,
)
from nostradamus_ioto_sdk.models.enums import StatOperation


@click.group(name="data")
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
@click.option(
    "--attributes",
    "-a",
    help="Comma-separated attribute names to select",
)
@click.option(
    "--filters",
    help='Filters as JSON array (e.g. \'[{"attribute":"temp","operator":"gt","value":20}]\')',
)
@click.option("--order-by", "-o", help="Attribute to order by")
@click.option("--nested", is_flag=True, default=False, help="Include nested data")
def data_get(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    project: str,
    collection: str,
    limit: Optional[int],
    attributes: Optional[str],
    filters: Optional[str],
    order_by: Optional[str],
    nested: bool,
) -> None:
    """Get data from collection.

    \b
    Examples:
      nioto data get -p PROJECT -c COLLECTION -n 10
      nioto data get -p PROJECT -c COLLECTION -a "temp,humidity"
      nioto data get -p PROJECT -c COLLECTION --filters '[{"attribute":"temp","operator":"gt","value":20}]'
    """
    try:
        client = get_client(api_key, base_url)

        attr_list = [a.strip() for a in attributes.split(",")] if attributes else None
        filter_list = None
        if filters:
            try:
                filter_list = json.loads(filters)
            except json.JSONDecodeError as e:
                console.print(f"[red]Invalid JSON filters:[/red] {e}")
                sys.exit(1)

        result = client.data.get(
            project_id=project,
            collection_id=collection,
            attributes=attr_list,
            filters=filter_list,
            order_by=order_by,
            limit=limit,
            nested=nested,
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


@data.command(name="statistics")
@api_key_option
@base_url_option
@format_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--collection", "-c", required=True, help="Collection ID")
@click.option(
    "--operation",
    "-op",
    required=True,
    type=click.Choice(["avg", "max", "min", "sum", "count", "distinct"]),
    help="Aggregation operation",
)
@click.option("--attribute", "-a", required=True, help="Attribute to aggregate")
@click.option("--group-by", "-g", help="Attribute to group by")
@click.option("--interval", "-i", help="Time interval for grouping")
@click.option("--limit", "-n", type=int, help="Limit results")
def data_statistics(
    api_key: Optional[str],
    base_url: Optional[str],
    output_format: str,
    project: str,
    collection: str,
    operation: str,
    attribute: str,
    group_by: Optional[str],
    interval: Optional[str],
    limit: Optional[int],
) -> None:
    """Get statistics/aggregations from collection.

    \b
    Examples:
      nioto data statistics -p PROJECT -c COLLECTION -op avg -a temperature
      nioto data statistics -p PROJECT -c COLLECTION -op count -a sensor_id -g region
    """
    try:
        client = get_client(api_key, base_url)
        op_enum = StatOperation(operation)
        result = client.data.statistics(
            project_id=project,
            collection_id=collection,
            operation=op_enum,
            attribute=attribute,
            group_by=group_by,
            interval=interval,
            limit=limit,
        )

        if output_format == "json":
            console.print_json(json.dumps(result, default=str))
        else:
            console.print(f"[cyan]Operation:[/cyan] {operation}({attribute})")
            if group_by:
                console.print(f"[cyan]Group by:[/cyan] {group_by}")
            console.print()
            console.print_json(json.dumps(result, default=str))
    except Exception as e:
        handle_error(e)


@data.command(name="delete")
@api_key_option
@base_url_option
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--collection", "-c", required=True, help="Collection ID")
@click.option("--key", "-k", help="Specific data key to delete")
@click.option("--from", "timestamp_from", help="Start of timestamp range (ISO 8601)")
@click.option("--to", "timestamp_to", help="End of timestamp range (ISO 8601)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def data_delete(
    api_key: Optional[str],
    base_url: Optional[str],
    project: str,
    collection: str,
    key: Optional[str],
    timestamp_from: Optional[str],
    timestamp_to: Optional[str],
    yes: bool,
) -> None:
    """Delete data from collection.

    \b
    At least one of --key, --from, or --to must be provided.

    \b
    Examples:
      nioto data delete -p PROJECT -c COLLECTION -k sensor_001
      nioto data delete -p PROJECT -c COLLECTION --from 2024-01-01T00:00:00Z --to 2024-02-01T00:00:00Z
    """
    try:
        if not key and not timestamp_from and not timestamp_to:
            console.print(
                "[red]Error:[/red] At least one of --key, --from, or --to must be provided.",
                style="bold",
            )
            sys.exit(1)

        if not yes:
            if not click.confirm("Delete data? This cannot be undone."):
                console.print("[yellow]Cancelled.[/yellow]")
                return

        client = get_client(api_key, base_url)
        result = client.data.delete(
            project_id=project,
            collection_id=collection,
            key=key,
            timestamp_from=timestamp_from,
            timestamp_to=timestamp_to,
        )

        console.print(f"[green]✓[/green] {result.get('message', 'Data deleted')}")
    except Exception as e:
        handle_error(e)
