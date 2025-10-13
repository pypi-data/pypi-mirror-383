from __future__ import annotations

from frogml._proto.qwak.deployment.deployment_pb2 import (
    AdvancedDeploymentOptions,
    KubeDeploymentType,
)
from frogml.core.exceptions import FrogmlException

from frogml_cli.commands.models.deployments.deploy.batch._logic.advanced_deployment_mapper import (
    batch_advanced_deployment_options_from_deploy_config,
)
from frogml_cli.commands.models.deployments.deploy.realtime._logic.advanced_deployment_mapper import (
    realtime_advanced_deployment_options_from_deploy_config,
)

ADVANCED_DEPLOYMENT_UNRECOGNIZED_TYPE_ERROR = (
    "The deployments type doesn't have an advanced deployments options configured"
)


def get_advanced_deployment_options_from_deploy_config(
    deploy_config, kube_deployment_type
) -> AdvancedDeploymentOptions:
    if kube_deployment_type == KubeDeploymentType.ONLINE:
        return realtime_advanced_deployment_options_from_deploy_config(deploy_config)
    elif kube_deployment_type == KubeDeploymentType.BATCH:
        return batch_advanced_deployment_options_from_deploy_config(deploy_config)
    elif kube_deployment_type == KubeDeploymentType.STREAM:
        return AdvancedDeploymentOptions()
    else:
        raise FrogmlException(ADVANCED_DEPLOYMENT_UNRECOGNIZED_TYPE_ERROR)
