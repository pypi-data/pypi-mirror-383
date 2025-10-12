from typing import Any, List, Optional

from ._internal import worker_queue
from .collectors.performance import PerformanceMonitor  # noqa: F401
from .instrumentation.limited_logger import limited_logger
from .schemas.events import CpuData
from .schemas.investigation import Investigation


def send_investigation_to_worker(investigation: Investigation[Any]) -> None:
    worker_queue.append(investigation)


class InvestigationsAggregator:
    def __init__(self) -> None:
        self.investigations: List[Investigation[Any]] = []

    def add_investigation(self, investigation: Investigation[Any]) -> None:
        self.investigations.append(investigation)

    def get_and_clear_investigations(self) -> List[Investigation[Any]]:
        investigations = [investigation for investigation in self.investigations]
        self.clear()
        return investigations

    def clear(self) -> None:
        self.investigations = []


performance_monitor: Optional[PerformanceMonitor] = None


def init_performance_monitor() -> None:
    global performance_monitor
    performance_monitor = PerformanceMonitor("investigation", None, 2)
    performance_monitor.save_cpu_snapshot()


def safe_get_cpu_usage() -> Optional[CpuData]:
    try:
        if performance_monitor is None:
            limited_logger.log("Performance monitor is not initialized")
            return None

        return performance_monitor.get_cpu_usage()
    except Exception:
        limited_logger.log("Error getting cpu usage", exc_info=True)
        return None


def safe_save_cpu_snapshot() -> None:
    try:
        if performance_monitor is None:
            limited_logger.log("Performance monitor is not initialized")
            return
        performance_monitor.save_cpu_snapshot()
    except Exception:
        limited_logger.log("Error updating cpu usage", exc_info=True)
        return None
