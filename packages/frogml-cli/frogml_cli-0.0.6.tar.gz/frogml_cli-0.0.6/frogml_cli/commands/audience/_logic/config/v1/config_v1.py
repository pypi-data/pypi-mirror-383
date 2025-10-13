from dataclasses import dataclass, field
from typing import List

from frogml._proto.qwak.audience.v1.audience_pb2 import Audience

from frogml_cli.commands.audience._logic.config.config_base import ConfigBase
from frogml_cli.commands.audience._logic.config.v1.spec import Spec


@dataclass
class ConfigV1(ConfigBase):
    spec: Spec = field(default_factory=Spec)

    def to_audiences_api(self) -> List[Audience]:
        return [
            Audience(
                name=audience_config.name,
                description=audience_config.description,
                routes=[route.to_route_api() for route in audience_config.routes],
                conditions=audience_config.conditions.to_conditions_api(),
            )
            for audience_config in self.spec.audiences
        ]
