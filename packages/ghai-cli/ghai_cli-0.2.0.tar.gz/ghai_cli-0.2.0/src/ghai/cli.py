"""Main CLI module for GHAI."""

import click

from ghai.commands.explain_issue import explain_issue
from ghai.commands.keys import keys
from ghai.commands.progress_update import progress_update
from ghai.commands.snippet_update import snippet_update


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """GHAI CLI - A Python command-line interface built with Click."""
    ctx.ensure_object(dict)


# Add commands to the main CLI group
cli.add_command(progress_update)
cli.add_command(keys)
cli.add_command(snippet_update)
cli.add_command(explain_issue)


def main() -> None:
    """Entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
