import time
from datetime import datetime, timedelta, timezone

from frogml._proto.qwak.builds.builds_pb2 import BuildStatus
from frogml.core.clients.build_orchestrator import BuildOrchestratorClient
from frogml.core.clients.logging_client import LoggingClient
from frogml.core.exceptions import FrogmlException

from frogml_cli.tools.colors import Color

INGESTED_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
# Ingested timestamp arrives with format "1900-01-01T00:00:00.000000000Z" but python doesn't support
# nanoseconds or Zulu
INGESTED_TIMESTAMP_MAXSIZE = 26
# Because the source of the timestamp truncates trailing zeros, we need to
# support two formats for the timestamp that is exactly on the second
ALTERNATIVE_INGESTED_TIMESTAMP_FORMAT_WITHOUT_DECIMALS = "%Y-%m-%dT%H:%M:%S"


class FrogmlLogHandling:
    TIME_UNITS = ["seconds", "minutes", "hours", "days"]
    FOLLOW_SLEEP_IF_NO_RESULTS_SECS = 5
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    BUILD_PENDING_STATUS = ["IN_PROGRESS", "REMOTE_BUILD_INITIALIZING"]
    BUILD_FINISHED_STATUS = [
        "INVALID",
        "SUCCESSFUL",
        "FAILED",
        "REMOTE_BUILD_CANCELLED",
        "REMOTE_BUILD_TIMED_OUT",
        "REMOTE_BUILD_UNKNOWN",
    ]

    def __init__(self):
        self.log_formatter = self.LogFormatting()

    @staticmethod
    def get_build_status_name(build_client, build_id: str):
        return BuildStatus.Name(build_client.get_build(build_id).build.build_status)

    def get_logs(
        self, follow, since, number_of_results, grep, source_params, source_name
    ):
        after = self.parse_since(since)
        after = after.strftime(self.TIME_FORMAT) if after is not None else after

        logging_client = LoggingClient()
        if source_name == "build":
            build_client = BuildOrchestratorClient()
        while True:
            params = {
                **source_params,
                "before_offset": None,
                "after_offset": after,
                "max_number_of_results": number_of_results,
                "log_text_filter": grep,
            }
            if source_name == "runtime_model":
                response = logging_client.read_model_runtime_logs(**params)
            elif source_name == "build":
                response = logging_client.read_build_logs(**params)
            else:
                raise FrogmlException(
                    f"Provided a non existing source name [{source_name}]"
                )

            if response.log_line:
                formatted_log_lines = self.log_formatter.format_logs(
                    response.log_line, without_instance_id=True
                )
                print("\n".join(formatted_log_lines), end="")
                after = response.last_offset
            elif follow:
                if source_name == "build":
                    build_status = self.get_build_status_name(
                        build_client, source_params["build_id"]
                    )
                    if build_status in self.BUILD_FINISHED_STATUS:
                        break
                time.sleep(self.FOLLOW_SLEEP_IF_NO_RESULTS_SECS)
            else:
                print("No logs returned")
                return

            if not follow:
                break

    def parse_since(self, since_sentence):
        if since_sentence is None:
            return None

        timedelta_params = {}
        split_line = since_sentence.split(" ")

        for base_index in range(0, len(split_line) - 1, 2):
            amount_string = split_line[base_index]
            if not amount_string.isdigit():
                raise FrogmlException(
                    "First word of [--since] must be a number representing "
                    "the amount of the time unit. (i.e. 3 minutes ago)"
                )
            time_unit = split_line[base_index + 1].lower()
            if time_unit not in self.TIME_UNITS:
                raise FrogmlException(
                    f"Must provide one of: {self.TIME_UNITS} to [--since] paramater. (i.e. 2 hours ago)"
                )
            timedelta_params[time_unit] = int(amount_string)

        return datetime.now(timezone.utc) - timedelta(**timedelta_params)

    class LogFormatting:
        def __init__(self):
            self.instance_color_map = {}
            self.colors = [
                Color.PURPLE,
                Color.CYAN,
                Color.DARKCYAN,
                Color.BLUE,
                Color.GREEN,
                Color.YELLOW,
                Color.WHITE,
                Color.GREY,
            ]

        def __format_datetime(self, timestamp_string):
            if timestamp_string.endswith("Z"):
                timestamp_string = timestamp_string[:-1]
            try:
                return f"{datetime.strptime(timestamp_string[:INGESTED_TIMESTAMP_MAXSIZE], INGESTED_TIMESTAMP_FORMAT)}\t"
            except ValueError:
                return f"{datetime.strptime(timestamp_string, ALTERNATIVE_INGESTED_TIMESTAMP_FORMAT_WITHOUT_DECIMALS)}\t"

        def format_logs(self, log_lines, without_instance_id: bool = False):
            colors_lines = []

            for line in log_lines:
                if line.source_instance_id not in self.instance_color_map:
                    source_id = len(self.instance_color_map) + 1
                    self.instance_color_map[line.source_instance_id] = {
                        "id": source_id,
                        "color": self.colors[source_id % len(self.colors)],
                    }

                instance_params = self.instance_color_map[line.source_instance_id]
                datetime_prefix = self.__format_datetime(line.ingested_iso_timestamp)
                prefix = ""
                if "level" in line.metadata:
                    prefix = f"{prefix}{line.metadata['level']} - "

                if "phase" in line.metadata:
                    prefix = f"{prefix}{line.metadata['phase']} - "

                if without_instance_id:
                    formatted_line = f'{instance_params["color"]}{datetime_prefix}{prefix}{line.text}{Color.END}'
                else:
                    formatted_line = f'{datetime_prefix}{instance_params["id"]} - {instance_params["color"]}{prefix}{line.text}{Color.END}'
                colors_lines.append(formatted_line)

            return colors_lines
