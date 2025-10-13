import click
from frogml.core.clients.model_management import ModelsManagementClient
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.deployments.deploy._logic.deploy_config import (
    DeployConfig,
)
from frogml_cli.commands.models.deployments.undeploy._logic.request_undeploy import (
    undeploy,
)
from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.inner.tools.config_handler import config_handler

logger = get_frogml_logger()


@click.command(
    name="undeploy",
    help="Model undeploy operation",
    cls=FrogMLCommand,
)
@click.option("--model-id", metavar="NAME", required=True, help="Model ID")
@click.option(
    "--variation-name",
    required=False,
    type=str,
    help="The variation name",
)
@click.option(
    "-f",
    "--from-file",
    help="Undeploy by run_config file, Command arguments will overwrite any run_config.",
    required=False,
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
)
@click.option(
    "--sync",
    is_flag=True,
    default=False,
    help="Waiting for deployments to be undeploy",
)
def models_undeploy(
    model_id: str,
    variation_name: str,
    from_file: str = None,
    sync: bool = False,
    **kwargs,
):
    logger.info(f"Initiating undeployment for model '{model_id}'")
    models_management = ModelsManagementClient()
    config: DeployConfig = config_handler(
        config=DeployConfig,
        from_file=from_file,
        out_conf=False,
        sections=("realtime",),
        model_id=model_id,
        variation_name=variation_name,
    )
    model_uuid = models_management.get_model_uuid(model_id)

    undeploy(model_id=model_id, config=config, model_uuid=model_uuid, sync=sync)
