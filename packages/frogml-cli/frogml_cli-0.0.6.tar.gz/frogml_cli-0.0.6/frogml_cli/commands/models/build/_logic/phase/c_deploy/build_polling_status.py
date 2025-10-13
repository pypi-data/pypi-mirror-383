from __future__ import annotations

import time

from frogml._proto.qwak.build.v1.build_api_pb2 import GetBuildResponse
from frogml._proto.qwak.build.v1.build_pb2 import BuildStatus

from frogml_cli.commands.models.build._logic.client_logs.messages import (
    FAILED_REMOTE_BUILD_SUGGESTION,
)
from frogml.core.inner.build_logic.interface.step_inteface import Step
from frogml.core.exceptions import FrogmlRemoteBuildFailedException


class BuildPollingStatusStep(Step):
    FINITE_BUILD_STATUSES = {
        BuildStatus.REMOTE_BUILD_CANCELLED,
        BuildStatus.REMOTE_BUILD_TIMED_OUT,
        BuildStatus.FAILED,
        BuildStatus.SUCCESSFUL,
    }
    SLEEP_BETWEEN_STATUS_CHECK = 10
    REMOTE_BUILD_FAILURE_EXCEPTION_FORMAT = "Your build failed with status {status}"

    def description(self) -> str:
        return "Polling on Build Status"

    def execute(self) -> None:
        self.build_logger.info("Waiting for build to finish")
        status = self.wait_for_finite_build_status()
        if status != BuildStatus.SUCCESSFUL:
            raise FrogmlRemoteBuildFailedException(
                message=self.REMOTE_BUILD_FAILURE_EXCEPTION_FORMAT.format(
                    status=BuildStatus.Name(status)
                ),
                suggestion=FAILED_REMOTE_BUILD_SUGGESTION.format(
                    base_url=self.context.platform_url,
                    build_id=self.context.build_id,
                    model_id=self.context.model_id,
                    project_uuid=self.context.project_uuid,
                ),
            )
        self.build_logger.info("Your build finished successfully")

    def wait_for_finite_build_status(self) -> BuildStatus:
        self.build_logger.spinner_text(line="Waiting for build to finish")
        while True:
            result: GetBuildResponse = (
                self.context.client_builds_orchestrator.get_build(self.context.build_id)
            )
            status: BuildStatus = result.build.build_status
            if status in self.FINITE_BUILD_STATUSES:
                return status
            self.build_logger.debug(f"Build status is currently {BuildStatus.Name(status)}")
            time.sleep(self.SLEEP_BETWEEN_STATUS_CHECK)
