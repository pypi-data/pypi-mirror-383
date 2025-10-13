import click

from frogml_cli.commands.models.describe._logic import execute_model_describe
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("describe", cls=FrogMLCommand)
@click.option("--model-id", metavar="NAME", help="Model ID")
@click.option(
    "--interface",
    metavar="",
    required=False,
    default=False,
    help="Returns the deployed build interface",
    is_flag=True,
)
@click.option(
    "--list-builds",
    metavar="",
    required=False,
    default=False,
    help="Returns the list of builds of model",
    is_flag=True,
)
@click.option(
    "--format",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json"], case_sensitive=True),
    metavar="FORMAT",
    required=False,
    help="The formatting style for commands output (choose from text, json)",
)
def model_describe(model_id, interface, list_builds, format, **kwargs):
    execute_model_describe(model_id, interface, list_builds, format)
