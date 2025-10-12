import itertools
import platform
import time
import types
from typing import Any, Dict, Iterable, Optional

from ...collectors.performance import PerformanceMonitor
from ...config import config
from ...investigation_manager import (
    safe_get_cpu_usage,
)
from ...native import RawExceptionExecution, RawInvestigation, set_investigation
from ...schemas.investigation import (
    InvestigationExceptionInfo,
    MachineMetrics,
    SystemInfo,
)
from ..limited_logger import limited_logger

total_investigations: int = 0
investigation_dedup: Dict[str, Dict[str, int]] = (
    dict()
)  # investigation_dedup[flow_id][dedup_key] = count


def open_investigation() -> Optional[RawInvestigation]:
    if not config.enable_investigation:
        return None

    raw_investigation = RawInvestigation(round(time.time() * 1000))
    set_investigation(raw_investigation)
    return raw_investigation


def get_total_investigations() -> int:
    return total_investigations


def increase_total_investigations() -> None:
    global total_investigations
    # That's not thread safe, but it's ok since this number is not really a hard limit. One off is not a big deal.
    total_investigations += 1


def get_investigation_dedup() -> Dict[str, Dict[str, int]]:
    return investigation_dedup


def reset_max_investigations() -> None:
    global total_investigations
    total_investigations = 0


def reset_investigation_dedup() -> None:
    global investigation_dedup
    investigation_dedup = dict()


def get_investigation_dedup_key(first_exception: RawExceptionExecution) -> str:
    key = f"{first_exception.name}"
    if (
        first_exception.exception_tracebacks is not None
        and isinstance(first_exception.exception_tracebacks, list)
        and len(first_exception.exception_tracebacks) > 0
    ):
        first_tracebacks = first_exception.exception_tracebacks[0]
        key += f":{first_tracebacks[0]}:{first_tracebacks[2]}"  # filename:line

    return key


def minimize_object_with_defaults(
    obj: Any,
) -> Any:
    return minimize_object(
        obj,
        config.investigation_max_object_depth,
        config.investigation_max_string_length,
        config.investigation_max_array_length,
        config.investigation_max_dict_length,
    )


def minimize_object(
    obj: Any,
    max_depth: int,
    max_string_length: int,
    max_array_length: int,
    max_dict_length: int,
) -> Any:
    try:
        if obj is None or isinstance(obj, (int, float, bool, complex)):
            return obj

        if isinstance(obj, str):
            return obj[:max_string_length]

        if max_depth < 0:
            return None

        if isinstance(obj, dict):
            return {
                minimize_object(
                    key,
                    max_depth - 1,
                    max_string_length,
                    max_array_length,
                    max_dict_length,
                ): minimize_object(
                    value,
                    max_depth - 1,
                    max_string_length,
                    max_array_length,
                    max_dict_length,
                )
                for key, value in itertools.islice(obj.items(), max_dict_length)
            }

        if isinstance(obj, types.GeneratorType):
            return None

        # Both dict and generator are iterable which we don't want to slice with `itertools.islice` since:
        # 1. Itertating through dict will return just the keys and not the values
        # 2. Iterating through generator will change it internal state
        if isinstance(obj, Iterable):
            return [
                minimize_object(
                    item,
                    max_depth - 1,
                    max_string_length,
                    max_array_length,
                    max_dict_length,
                )
                for item in itertools.islice(obj, max_array_length)
            ]

    except Exception:
        pass

    # Drop anythig else including functions, Classes, etc
    return None


def minimize_exception_info_in_place(
    exception_info: InvestigationExceptionInfo,
) -> InvestigationExceptionInfo:
    exception_info.message = minimize_object_with_defaults(exception_info.message)
    return exception_info


def get_pod_name() -> Optional[str]:
    try:
        return platform.node()
    except Exception:
        return None


def get_node_name() -> Optional[str]:
    try:
        with open("/etc/machine-id", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_system_info() -> SystemInfo:
    return SystemInfo(
        pod_name=get_pod_name(),
        node_name=get_node_name(),
    )


def get_machine_metrics() -> Optional[MachineMetrics]:
    try:
        return MachineMetrics(
            cpu=safe_get_cpu_usage(),
            memory=PerformanceMonitor.get_memory_usage(),
            threads_count=PerformanceMonitor.get_thread_count(),
        )
    except Exception:
        limited_logger.log("Error getting machine metrics", exc_info=True)
        return None
