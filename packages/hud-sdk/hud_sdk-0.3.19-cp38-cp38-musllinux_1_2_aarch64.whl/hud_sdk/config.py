import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union  # noqa: F401
from uuid import UUID

DEFAULT_HUD_HOST = "https://api-prod.hud.io"
DEFAULT_CLIENT = "http"
DEFAULT_DEBUG_PREFIX = "[HUD]"
DEFAULT_JSON_PATH = "hud.json"

ENABLE_INVESTIGATION_VARIABLE = "HUD_ENABLE_INVESTIGATION"


class Config:
    def __init__(self) -> None:
        self.host = os.environ.get("HUD_HOST", DEFAULT_HUD_HOST)
        self.logs_queue_size = int(os.environ.get("HUD_LOGS_QUEUE_SIZE", 4000))
        self.batch_size = int(os.environ.get("HUD_BATCH_SIZE", 100))
        self.process_queue_flush_interval = int(
            os.environ.get("HUD_PROCESS_QUEUE_FLUSH_INTERVAL", 1)
        )
        self.logs_flush_interval = int(
            os.environ.get("HUD_LOGS_QUEUE_FLUSH_INTERVAL", 60)
        )
        self.invocations_flush_interval = int(
            os.environ.get("HUD_INVOCATIONS_FLUSH_INTERVAL", 30)
        )
        self.invocations_first_send_delay = int(
            os.environ.get("HUD_INVOCATIONS_FIRST_SEND_DELAY", 30)
        )
        self.workload_data_flush_interval = int(
            os.environ.get("HUD_WORKLOAD_DATA_FLUSH_INTERVAL", 5 * 60)
        )
        self.modules_report_interval = int(
            os.environ.get("HUD_MODULES_REPORT_INTERVAL", 60 * 60)
        )
        self.performance_report_interval = int(
            os.environ.get("HUD_PERFORMANCE_REPORT_INTERVAL", 5 * 60)
        )
        self.declarations_flush_interval = int(
            os.environ.get("HUD_DECLARATIONS_FLUSH_INTERVAL", 30)
        )
        self.investigations_flush_interval = int(
            os.environ.get("HUD_INVESTIGATIONS_FLUSH_INTERVAL", 5)
        )
        self.api_max_retries = int(os.environ.get("HUD_API_MAX_RETRIES", 3))
        self.api_backoff_factor = float(os.environ.get("HUD_API_BACKOFF_FACTOR", 1.2))
        self.api_timeout = float(os.environ.get("HUD_API_TIMEOUT", 10))  # seconds
        self.debug_prefix = os.environ.get("HUD_DEBUG_PREFIX", DEFAULT_DEBUG_PREFIX)
        self.client_type = os.environ.get("HUD_CLIENT", DEFAULT_CLIENT)
        self.json_path = os.environ.get("HUD_JSON_PATH", DEFAULT_JSON_PATH)
        self.max_file_size = int(os.environ.get("HUD_MAX_FILE_SIZE", 2 * 1024 * 1024))
        self.max_instrumented_functions = int(
            os.environ.get("HUD_MAX_INSTRUMENTED_FUNCTIONS", 50 * 1000)
        )
        self.min_memory_required_mb = int(
            os.environ.get("HUD_MIN_MEMORY_REQUIRED", 250)
        )
        self.max_processes = int(os.environ.get("HUD_MAX_PROCESSES", 200))

        self.run_after_fork = sys.platform == "linux" and os.environ.get(
            "HUD_SUPPORT_FORK", "true"
        ).lower() in [
            "true",
            "1",
        ]

        self.hud_dependency_blacklist = {
            "hud_sdk",
            "requests",
            "charset-normalizer"  # From requests
            "idna",  # From requests
            "urllib3",  # From requests
            "certifi",  # From requests
            "psutil",
            "orjson",
        }
        modules_to_trace_str = os.environ.get("HUD_MODULES_TO_TRACE")
        include_modules_str = os.environ.get("HUD_INCLUDE_MODULES")
        self.modules_to_trace = set(
            modules_to_trace_str.split(",")
            if modules_to_trace_str
            else [] + include_modules_str.split(",") if include_modules_str else []
        )
        self.blacklisted_modules = ["ddtrace", "opentelemetry-instrumentation"]
        self.log_level = os.environ.get("HUD_LOG_LEVEL", "INFO")
        self.verbose_logs = os.environ.get("HUD_VERBOSE", "").lower() in ["true", "1"]
        self.debug_logs = os.environ.get("HUD_DEBUG", "").lower() in ["true", "1"]
        self.pretty_logs = os.environ.get("HUD_PRETTY_LOGS", "false").lower() in [
            "true",
            "1",
        ]
        self.aws_metadata_server = os.environ.get(
            "HUD_AWS_METADATA_SERVER", "169.254.169.254"
        )
        self.aws_metadata_timeout = float(os.environ.get("HUD_AWS_METADATA_TIMEOUT", 5))
        self.aws_local_metadata_file = os.environ.get(
            "HUD_AWS_LOCAL_METADATA_FILE", "/run/cloud-init/instance-data.json"
        )
        self.disable_exception_handler = os.environ.get(
            "HUD_DISABLE_EXCEPTION_HANDLER", ""
        ).lower() in ["true", "1"]
        self.sketch_bin_width = float(os.environ.get("HUD_SKETCH_BIN_WIDTH", 1.2))
        self.log_performance = os.environ.get(
            "HUD_LOG_PERFORMANCE", "true"
        ).lower() not in [
            "false",
            "0",
        ]
        self.log_runtime = os.environ.get("HUD_LOG_RUNTIME", "true").lower() not in [
            "false",
            "0",
        ]

        self.instrument_fastapi = os.environ.get(
            "HUD_INSTRUMENT_FASTAPI", "true"
        ).lower() not in [
            "false",
            "0",
        ]
        self.instrument_flask = os.environ.get(
            "HUD_INSTRUMENT_FLASK", "true"
        ).lower() not in [
            "false",
            "0",
        ]
        self.instrument_django = os.environ.get(
            "HUD_INSTRUMENT_DJANGO", "true"
        ).lower() not in [
            "false",
            "0",
        ]
        self.instrument_tornado = os.environ.get(
            "HUD_INSTRUMENT_TORNADO", "true"
        ).lower() not in [
            "false",
            "0",
        ]
        self.instrument_aiokafka = os.environ.get(
            "HUD_INSTRUMENT_AIOKAFKA", "true"
        ).lower() not in [
            "false",
            "0",
        ]
        self.instrument_arq = os.environ.get(
            "HUD_INSTRUMENT_ARQ", "true"
        ).lower() not in [
            "false",
            "0",
        ]

        self.user_ca_bundle = os.environ.get("HUD_CA_BUNDLE", None)
        self.user_cert = os.environ.get("HUD_SSL_CERT_FILE", None)

        self.uuid_namespace = UUID("f253e6fb-3f25-412c-907d-dbbbcc3f51c0}")
        self.sdk_name = "hud_sdk"

        self.worker_check_queues_interval = 60
        self.worker_session_id_check_interval = 5
        self.worker_session_id_timeout = 60

        self.exporter_start_timeout = 30
        self.exporter_minimum_start_timeout = 5
        self.exporter_service_registered_timeout = 10
        self.exporter_is_up_check_interval = 30
        self.exporter_shared_memory_size = 50_000_000
        self.exporter_process_registry_warmup_period = int(
            os.environ.get("HUD_EXPORTER_PROCESS_REGISTRY_WARMUP_PERIOD", 6)
        )
        self.exporter_process_registry_update_interval = 1
        self.exporter_queue_process_interval = 1
        self.exporter_manager_check_interval = 10
        self.exporter_disabled_check_interval = 1
        self.exporter_status_lock_acquisition_timeout = 5
        self.exporter_already_running_status_code = 23
        self.exporter_unique_id = os.environ.get("HUD_EXPORTER_UNIQUE_ID", None)
        self.exporter_stop_running_tasks_grace = 8

        self.manager_lock_warning_threshold = 1
        self.manager_lock_critical_threshold = 10
        self.manager_lock_owner_check_interval = 10
        self.manager_leaked_queue_check_interval = 10

        self.manager_password = b"password"
        self.manager_initialization_timeout = 15
        self.session_id_refresh_interval = 2

        self.shared_memory_utilization_warning_threshold = 50
        self.shared_memory_utilization_critical_threshold = 80

        self.python_binary = os.environ.get(
            "HUD_PYTHON_BINARY_PATH", None
        )  # type: Optional[str]

        self.hud_directory = self._get_hud_directory()
        self.hud_exporter_status_file = os.path.join(
            self.hud_directory, "exporter_status"
        )

        self.wait_for_manager_port_timeout = 30
        self.min_time_for_manager_port = 5
        self.num_of_worker_exporter_queues = 3

        self.worker_configuration_update_check_interval = 60
        self.exporter_configuration_update_check_interval = 5 * 60
        self.keepalive_interval = 300

        self.suppressed_event_types = []  # type: List[str]
        self.use_hud_pyc = (
            sys.version_info >= (3, 6)
            and sys.version_info < (3, 14)
            and os.environ.get("HUD_DISABLE_HUD_PYC", "false").lower() != "true"
        )

        self.max_investigations = 25
        self.max_investigations_time_window_seconds = 60 * 60 * 6  # 6 hours
        self.max_same_investigation = 2
        self.max_same_investigations_time_window_seconds = 60 * 60 * 6  # 6 hours

        self.investigation_max_object_depth = 10
        self.investigation_max_string_length = 1024
        self.investigation_max_array_length = 100
        self.investigation_max_dict_length = 100
        self.investigation_max_body_length = 1024 * 10
        self.investigation_censor_regexes: List[Tuple[str, str]] = []
        self.investigation_censor_black_list_params: List[str] = []
        self.investigation_max_same_log = 10
        self.investigation_whitelist_nested_keys: List[str] = []
        self.investigation_blacklist_nested_keys: List[str] = []
        self.enable_investigation = (
            os.environ.get(ENABLE_INVESTIGATION_VARIABLE) == "true"
        )
        self.investigation_performance_monitor_interval = 10
        # This should be set last
        self.updatable_configuration = {
            "logs_flush_interval": self.logs_flush_interval,
            "invocations_flush_interval": self.invocations_flush_interval,
            "modules_report_interval": self.modules_report_interval,
            "performance_report_interval": self.performance_report_interval,
            "declarations_flush_interval": self.declarations_flush_interval,
            "suppressed_event_types": self.suppressed_event_types,
            "keepalive_interval": self.keepalive_interval,
            "max_investigations": self.max_investigations,
            "max_investigations_time_window_seconds": self.max_investigations_time_window_seconds,
            "max_same_investigation": self.max_same_investigation,
            "max_same_investigations_time_window_seconds": self.max_same_investigations_time_window_seconds,
            "investigation_max_object_depth": self.investigation_max_object_depth,
            "investigation_max_string_length": self.investigation_max_string_length,
            "investigation_max_array_length": self.investigation_max_array_length,
            "investigation_max_dict_length": self.investigation_max_dict_length,
            "investigation_max_body_length": self.investigation_max_body_length,
            "investigation_censor_regexes": self.investigation_censor_regexes,
            "investigation_censor_black_list_params": self.investigation_censor_black_list_params,
            "investigation_max_same_log": self.investigation_max_same_log,
            "investigation_whitelist_nested_keys": self.investigation_whitelist_nested_keys,
            "investigation_blacklist_nested_keys": self.investigation_blacklist_nested_keys,
            "enable_investigation": self.enable_investigation,
            "investigation_performance_monitor_interval": self.investigation_performance_monitor_interval,
        }

        self.standby_check_minimum_interval = 5

        self.init_timeout = 30

    def _update_updatable_keys(
        self, new_config: Dict[str, Union[List[str], int]]
    ) -> None:
        for key, value in self.updatable_configuration.items():
            if key in new_config:
                setattr(self, key, new_config[key])
            else:
                # if the key is not in the new config, set it to the default value
                setattr(self, key, value)

        investigation_env_var = os.environ.get(ENABLE_INVESTIGATION_VARIABLE)
        if investigation_env_var is not None:
            self.enable_investigation = investigation_env_var == "true"

    def _get_hud_directory(self) -> str:
        home_dir = Path.home()
        if sys.platform == "darwin":
            return str(home_dir / "Library" / "hud" / "exporters")
        if sys.platform == "win32":
            return str(home_dir / "AppData" / "hud" / "exporters")
        return str(home_dir / ".hud" / "exporters")


config = Config()
