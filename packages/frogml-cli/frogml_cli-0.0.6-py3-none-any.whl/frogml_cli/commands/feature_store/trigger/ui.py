import click
from frogml._proto.qwak.feature_store.features.feature_set_service_pb2 import (
    RunBatchFeatureSetResponse,
)
from frogml.core.clients.feature_store import FeatureRegistryClient
from frogml.core.exceptions import FrogmlException

from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.colors import Color


@click.command(
    "trigger", cls=FrogMLCommand, help="Trigger a batch feature set job ingestion job"
)
@click.argument("name")
def trigger_feature_set(name, **kwargs):
    """
    Trigger a batch feature set ingestion job

    Args:
        name: Feature set name that will be triggered.
    """
    try:
        result: RunBatchFeatureSetResponse = FeatureRegistryClient().run_feature_set(
            feature_set_name=name
        )
    except Exception as e:
        print(
            f"{Color.RED} Failed to trigger a batch feature set ingestion for feature set {name} {Color.END}"
        )
        raise FrogmlException(
            f"Failed to trigger a batch feature set ingestion for feature set {name}"
        ) from e

    print(
        f"{Color.GREEN}Successfully triggered a batch feature set ingestion for feature set: {Color.YELLOW}{name}"
    )
    if result.execution_id:
        print(f"{Color.WHITE} Execution ID: {Color.YELLOW}{result.execution_id}")
