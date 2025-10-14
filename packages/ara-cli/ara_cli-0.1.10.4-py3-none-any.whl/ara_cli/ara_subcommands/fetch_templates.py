import typer
from .common import MockArgs
from ara_cli.ara_command_action import fetch_templates_action


def fetch_templates_main():
    """Fetches templates and stores them in .araconfig."""
    args = MockArgs()
    fetch_templates_action(args)


def register(parent: typer.Typer):
    help_text = "Fetches templates and stores them in .araconfig"
    parent.command(name="fetch-templates", help=help_text)(fetch_templates_main)
