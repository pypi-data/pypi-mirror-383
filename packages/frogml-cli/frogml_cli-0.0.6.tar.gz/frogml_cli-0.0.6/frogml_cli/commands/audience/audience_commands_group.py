import logging

import click

from frogml_cli.commands.audience.create.ui import create_audience_command
from frogml_cli.commands.audience.delete.ui import delete_audience_command
from frogml_cli.commands.audience.get.ui import get_audience_command
from frogml_cli.commands.audience.list.ui import list_audience_command
from frogml_cli.commands.audience.update.ui import update_audience_command

logger = logging.getLogger(__name__)
DELIMITER = "----------------------------------------"

AUTOMATION = "automation"


@click.group(
    name="audiences",
    help="Manage audiences",
)
def audience_commands_group():
    # Click commands group injection
    pass


audience_commands_group.add_command(create_audience_command)
audience_commands_group.add_command(get_audience_command)
audience_commands_group.add_command(list_audience_command)
audience_commands_group.add_command(delete_audience_command)
audience_commands_group.add_command(update_audience_command)
