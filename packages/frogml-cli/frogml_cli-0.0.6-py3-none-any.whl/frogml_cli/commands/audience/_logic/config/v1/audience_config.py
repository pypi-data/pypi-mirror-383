from dataclasses import dataclass, field
from typing import List

from frogml._proto.qwak.audience.v1.audience_pb2 import AudienceRoutesEntry

from frogml_cli.commands.audience._logic.config.v1.conditions_config import (
    ConditionsConfig,
)
from frogml_cli.commands.audience._logic.config.v1.route_config import RouteConfig


@dataclass
class AudienceConfig:
    name: str = field(default="")
    id: str = field(default="")
    description: str = field(default="")
    routes: List[RouteConfig] = field(default_factory=list)
    conditions: ConditionsConfig = field(default_factory=ConditionsConfig)

    def to_audience_route_entry(self, index: int = 0) -> AudienceRoutesEntry:
        return AudienceRoutesEntry(
            audience_id=self.id,
            audience_name=self.name,
            order=index + 1,
            routes=[route.to_route_api() for route in self.routes],
        )
