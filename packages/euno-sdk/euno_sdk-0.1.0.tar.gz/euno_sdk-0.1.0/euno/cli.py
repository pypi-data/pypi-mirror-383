"""
Command-line interface for the Euno SDK.

This module provides the CLI functionality accessible via the 'euno' command.
"""

import click
from .core import hello_world, get_version


@click.group()
@click.version_option(version=get_version(), prog_name="euno-sdk")
def main():
    """
    Euno SDK - A Python library and CLI tool for interacting with Euno instances.
    
    This tool provides both programmatic access to Euno functionality
    and a command-line interface for common operations.
    """
    pass


@main.command()
@click.option('--name', '-n', default='World', help='Name to greet')
def hello_world_cmd(name: str):
    """
    A simple hello world command to demonstrate the CLI.
    
    Example:
        euno hello-world --name Euno
    """
    message = hello_world(name)
    click.echo(message)


@main.command()
def version():
    """Show the version of the Euno SDK."""
    click.echo(f"Euno SDK version: {get_version()}")


if __name__ == '__main__':
    main()
