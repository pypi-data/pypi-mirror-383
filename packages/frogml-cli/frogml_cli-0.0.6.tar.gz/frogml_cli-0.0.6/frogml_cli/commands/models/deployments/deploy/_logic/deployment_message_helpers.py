from __future__ import annotations

from typing import Dict

from frogml._proto.qwak.deployment.deployment_pb2 import (
    BatchConfig,
    EnvironmentDeploymentMessage,
    HostingService,
    KubeDeployment,
    KubeDeploymentType,
    ServingStrategy,
)
from frogml.core.clients.administration.eco_system.client import EcosystemClient
from frogml.core.clients.instance_template.client import (
    InstanceTemplateManagementClient,
)
from frogml.core.exceptions import FrogmlException

from frogml_cli.commands.models.deployments.deploy._logic.advance_deployment_options_handler import (
    get_advanced_deployment_options_from_deploy_config,
)
from frogml_cli.commands.models.deployments.deploy._logic.deploy_config import (
    DeployConfig,
)
from frogml_cli.commands.models.deployments.deploy._logic.deployment_size_mapper import (
    deployment_size_from_deploy_config,
)
from frogml_cli.commands.models.deployments.deploy.realtime._logic.serving_strategy_mapper import (
    create_realtime_serving_strategy_from_deploy_config,
)
from frogml_cli.commands.models.deployments.deploy.streaming._logic.serving_strategy_mapper import (
    create_streaming_serving_strategy_from_deploy_config,
)
from frogml_cli.inner.tools.cli_tools import dictify_params

UNKNOWN_SERVING_STRATEGY = (
    "The deployments type doesn't have a serving strategy configured"
)


def get_env_to_deployment_message(
    deploy_config: DeployConfig,
    kube_deployment_type: KubeDeploymentType,
    ecosystem_client: EcosystemClient,
    instance_template_client: InstanceTemplateManagementClient,
) -> Dict[str, EnvironmentDeploymentMessage]:
    deployment_size = deployment_size_from_deploy_config(
        deploy_config, instance_template_client, ecosystem_client
    )
    advanced_deployment_options = get_advanced_deployment_options_from_deploy_config(
        deploy_config, kube_deployment_type
    )
    environment_variables = {}

    if len(deploy_config.realtime.environments) != 0:
        deploy_config.environments = deploy_config.realtime.environments

    environment_name_to_config = ecosystem_client.get_environments_names_to_details(
        deploy_config.environments
    )

    if kube_deployment_type == KubeDeploymentType.ONLINE:
        env_to_serving_strategy = create_realtime_serving_strategy_from_deploy_config(
            deploy_config,
            environment_name_to_config,
        )
        environment_variables = dictify_params(deploy_config.realtime.env_vars)
    elif kube_deployment_type == KubeDeploymentType.BATCH:
        env_to_serving_strategy = {}
        if len(environment_name_to_config) == 0:
            env_to_serving_strategy = {
                ecosystem_client.get_account_details().default_environment_id: ServingStrategy(
                    batch_config=BatchConfig()
                )
            }
        else:
            for env_name, env_config in environment_name_to_config.items():
                env_to_serving_strategy[env_config.id] = ServingStrategy(
                    batch_config=BatchConfig()
                )

    elif kube_deployment_type == KubeDeploymentType.STREAM:
        env_to_serving_strategy = {}
        if len(environment_name_to_config) == 0:
            env_to_serving_strategy[
                ecosystem_client.get_account_details().default_environment_id
            ] = create_streaming_serving_strategy_from_deploy_config(deploy_config)
        else:
            for env_name, env_config in environment_name_to_config.items():
                env_to_serving_strategy[
                    env_config.id
                ] = create_streaming_serving_strategy_from_deploy_config(deploy_config)
        environment_variables = dictify_params(deploy_config.stream.env_vars)
    else:
        raise FrogmlException(UNKNOWN_SERVING_STRATEGY)
    env_to_hosting_services = {
        env_id: HostingService(
            kube_deployment=KubeDeployment(
                deployment_size=deployment_size,
                advanced_deployment_options=advanced_deployment_options,
                serving_strategy=serving_strategy,
                kube_deployment_type=kube_deployment_type,
                environment_variables=environment_variables,
            ),
        )
        for env_id, serving_strategy in env_to_serving_strategy.items()
    }
    env_deployment_messages = {
        env_id: EnvironmentDeploymentMessage(
            model_id=deploy_config.model_id,
            build_id=deploy_config.build_id,
            hosting_service=hosting_service,
        )
        for env_id, hosting_service in env_to_hosting_services.items()
    }
    return env_deployment_messages
