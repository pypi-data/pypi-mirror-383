"""
Resources commands for the Euno SDK.

This module provides commands for interacting with Euno data model resources.
"""

import click
import json
import csv
import io
from typing import List, Optional, Dict, Any
from .config import config
from .api import api_client


def list_resources_command(
    eql: Optional[str] = None,
    properties: str = "uri,type,name",
    page: int = 1,
    page_size: int = 50,
    sorting: Optional[str] = None,
    relationships: Optional[str] = None,
    format: str = "json",
) -> None:
    """
    List resources from the Euno data model.

    Args:
        eql: Euno Query Language expression
        properties: Comma-separated list of properties (default: uri,type,name)
        page: Page number (default: 1)
        page_size: Number of resources per page (default: 50)
        sorting: Sorting specification
        relationships: Comma-separated list of relationships
        format: Output format - json, csv, or pretty (default: json)
    """
    if not config.is_configured():
        click.echo("❌ Euno SDK is not configured. Run 'euno init' to get started.")
        return

    token = config.get_token()
    account_id = config.get_account_id()

    if not account_id:
        click.echo("❌ No account ID configured. Run 'euno init' to set up your account.")
        return

    if not token:
        click.echo("❌ No token configured. Run 'euno init' to set up your account.")
        return

    # Prepare parameters
    params: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
        "include_count": True,
    }

    # Add optional parameters if provided
    if eql:
        params["eql"] = [eql]

    # Always add properties (now has default value)
    params["properties"] = properties.split(",")

    if sorting:
        params["sorting"] = sorting.split(",")
    if relationships:
        params["relationships"] = relationships.split(",")

    try:
        response = api_client.search_resources(token, account_id, params)

        # Format and display results
        if format == "json":
            click.echo(json.dumps(response, indent=2))
        elif format == "csv":
            requested_props = params.get("properties")
            _display_csv(response, requested_props)
        elif format == "pretty":
            _display_pretty(response)
        else:
            click.echo(f"❌ Unknown format: {format}. Supported formats: json, csv, pretty")

    except Exception as e:
        click.echo(f"❌ Error searching resources: {str(e)}")


def _display_csv(response: Dict[str, Any], requested_properties: Optional[List[str]] = None) -> None:
    """Display search results in CSV format."""
    resources = response.get("resources", [])
    if not resources:
        click.echo("No resources found.")
        return

    # Determine property order
    if requested_properties:
        # Use the order specified in the request
        properties = requested_properties
    else:
        # Get all unique property names from the resources and sort alphabetically
        all_properties = set()
        for resource in resources:
            all_properties.update(resource.keys())
        properties = sorted(list(all_properties))

    # Create CSV output
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(properties)

    # Write data rows
    for resource in resources:
        row = [resource.get(prop, "") for prop in properties]
        writer.writerow(row)

    click.echo(output.getvalue())


def _display_pretty(response: Dict[str, Any]) -> None:
    """Display search results in a pretty table format."""
    resources = response.get("resources", [])
    count = response.get("count", 0)

    if not resources:
        click.echo("No resources found.")
        return

    click.echo(f"Found {count} resources (showing {len(resources)}):")
    click.echo()

    # Get all unique property names
    all_properties = set()
    for resource in resources:
        all_properties.update(resource.keys())

    # Convert to sorted list, prioritizing common properties
    priority_props = ["uri", "type", "name"]
    properties = []

    # Add priority properties first if they exist
    for prop in priority_props:
        if prop in all_properties:
            properties.append(prop)
            all_properties.remove(prop)

    # Add remaining properties
    properties.extend(sorted(all_properties))

    # Calculate column widths
    col_widths = {}
    for prop in properties:
        col_widths[prop] = max(len(prop), max(len(str(resource.get(prop, ""))) for resource in resources))
        col_widths[prop] = min(col_widths[prop], 50)  # Cap at 50 characters

    # Print header
    header = " | ".join(prop.ljust(col_widths[prop]) for prop in properties)
    click.echo(header)
    click.echo("-" * len(header))

    # Print data rows
    for resource in resources:
        row = []
        for prop in properties:
            value = str(resource.get(prop, ""))
            if len(value) > 50:
                value = value[:47] + "..."
            row.append(value.ljust(col_widths[prop]))
        click.echo(" | ".join(row))
