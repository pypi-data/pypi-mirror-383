from typing import Literal

import click
from frogml._proto.qwak.models.models_pb2 import (
    DeploymentModelStatus,
    ListModelsResponse,
    Model,
)

from frogml_cli.commands.models.list_models._logic import list_models as _list_models
from frogml_cli.commands.ui_tools import output_as_json, output_as_table
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


def parse_model(model: Model) -> list[str]:
    return [
        model.model_id,
        model.uuid,
        model.display_name,
        model.model_description,
        model.project_id,
        model.created_by,
        model.created_at,
        model.last_modified_by,
        model.last_modified_at,
        model.model_status,
        "\n".join(
            [f"{branch.branch_name} {branch.branch_id}" for branch in model.branches]
        ),
        DeploymentModelStatus.DESCRIPTOR.values_by_number[
            model.deployment_model_status
        ].name,
    ]


@click.command("list-models", cls=FrogMLCommand)
@click.option("--project-key", metavar="NAME", required=True, help="JFrog Project key")
@click.option(
    "--format",
    "output_format",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json"], case_sensitive=True),
    metavar="FORMAT",
    required=False,
    help="The formatting style for command output (choose from text, json)",
)
def list_models(project_key: str, output_format: Literal["text", "json"]):
    model_list_result: ListModelsResponse = _list_models(project_key)
    columns: list[str] = [
        "Model id",
        "Model UUID",
        "Model Name",
        "Model Description",
        "Project ID",
        "Created By",
        "Created At",
        "Last Modified At",
        "Last Modified By",
        "Model Status",
        "Branches",
        "Deployment Status",
    ]

    if output_format == "json":
        output_as_json(model_list_result)
    else:  # output_format == "text"
        output_as_table(model_list_result.models, parse_model, headers=columns)
