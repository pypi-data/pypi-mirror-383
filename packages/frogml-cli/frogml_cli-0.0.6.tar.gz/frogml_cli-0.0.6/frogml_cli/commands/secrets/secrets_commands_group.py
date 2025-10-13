import click

from frogml_cli.commands.secrets.delete.ui import delete_secret
from frogml_cli.commands.secrets.get.ui import get_secret
from frogml_cli.commands.secrets.set.ui import set_secret


@click.group(
    "secrets",
    help="Commands for interacting with the secret store",
)
def secrets_commands_group():
    # Click commands group injection
    pass


secrets_commands_group.add_command(set_secret)
secrets_commands_group.add_command(get_secret)
secrets_commands_group.add_command(delete_secret)
