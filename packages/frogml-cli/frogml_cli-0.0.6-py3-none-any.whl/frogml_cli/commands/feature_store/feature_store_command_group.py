import click

from frogml_cli.commands.feature_store.backfill.ui import backfill
from frogml_cli.commands.feature_store.delete.ui import delete_fs_object
from frogml_cli.commands.feature_store.execution.ui import execution_status
from frogml_cli.commands.feature_store.list.ui import list_feature_sets
from frogml_cli.commands.feature_store.pause.ui import pause_feature_set
from frogml_cli.commands.feature_store.register.ui import register_fs_objects
from frogml_cli.commands.feature_store.resume.ui import resume_feature_set
from frogml_cli.commands.feature_store.trigger.ui import trigger_feature_set


@click.group(
    name="features",
    help="Commands for interacting with JFrogML Feature Store",
)
def feature_store_commands_group():
    # Click commands group injection
    pass


feature_store_commands_group.add_command(delete_fs_object)
feature_store_commands_group.add_command(list_feature_sets)
feature_store_commands_group.add_command(pause_feature_set)
feature_store_commands_group.add_command(resume_feature_set)
feature_store_commands_group.add_command(trigger_feature_set)
feature_store_commands_group.add_command(register_fs_objects)
feature_store_commands_group.add_command(backfill)
feature_store_commands_group.add_command(execution_status)
