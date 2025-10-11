"""
Command-line interface for the Euno SDK.

This module provides the CLI functionality accessible via the 'euno' command.
"""

import click
from .core import hello_world, get_version
from .auth import init_command, status_command, logout_command
from .resources import list_resources_command


@click.group()
@click.version_option(version=get_version(), prog_name="euno-sdk")
def main() -> None:
    """
    Euno SDK - A Python library and CLI tool for interacting with Euno instances.

    This tool provides both programmatic access to Euno functionality
    and a command-line interface for common operations.
    """
    pass


@main.command()
@click.option("--name", "-n", default="World", help="Name to greet")
def hello_world_cmd(name: str) -> None:
    """
    A simple hello world command to demonstrate the CLI.

    Example:
        euno hello-world --name Euno
    """
    message = hello_world(name)
    click.echo(message)


@main.command()
def version() -> None:
    """Show the version of the Euno SDK."""
    click.echo(f"Euno SDK version: {get_version()}")


@main.command()
def init() -> None:
    """
    Initialize the Euno SDK with your API token.

    This command will prompt you for your Euno API token and validate it
    against the Euno backend. The token will be stored securely for future use.

    Example:
        euno init
    """
    init_command()


@main.command()
def status() -> None:
    """
    Show the current configuration status.

    Displays information about the current configuration including
    backend URL, token status, and user information.

    Example:
        euno status
    """
    status_command()


@main.command()
def logout() -> None:
    """
    Clear the stored configuration and log out.

    This will remove the stored API token and require you to run
    'euno init' again to authenticate.

    Example:
        euno logout
    """
    logout_command()


@main.group()
def resources() -> None:
    """Commands for working with Euno data model resources."""
    pass


@resources.command("list")
@click.option("--eql", "-e", help="Euno Query Language expression")
@click.option(
    "--properties",
    "-p",
    default="uri,type,name",
    help="Comma-separated list of properties (default: uri,type,name)",
)
@click.option("--page", default=1, help="Page number (default: 1)")
@click.option("--page-size", default=50, help="Number of resources per page (default: 50)")
@click.option("--sorting", "-s", help="Sorting specification")
@click.option("--relationships", "-r", help="Comma-separated list of relationships")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "pretty"]),
    help="Output format (default: json)",
)
def list_resources(
    eql: str,
    properties: str,
    page: int,
    page_size: int,
    sorting: str,
    relationships: str,
    output_format: str,
) -> None:
    """
    List resources from the Euno data model.

    Examples:
        euno resources list
        euno resources list --eql "has child(true, 1)" --properties "uri,name,type" \
            --format pretty
        euno resources list --relationships "parent,child" --page-size 20
    """
    list_resources_command(
        eql=eql,
        properties=properties,
        page=page,
        page_size=page_size,
        sorting=sorting,
        relationships=relationships,
        format=output_format,
    )


if __name__ == "__main__":
    main()
