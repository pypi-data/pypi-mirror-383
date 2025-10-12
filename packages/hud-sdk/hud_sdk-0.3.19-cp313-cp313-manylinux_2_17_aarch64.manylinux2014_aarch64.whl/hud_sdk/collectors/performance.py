import gc
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

import psutil

from ..schemas.events import CpuData, MemoryData, Performance


class PerformanceMonitor:
    def __init__(
        self,
        owner: str,
        pod_cpu_limit: Optional[str] = None,
        cpu_stats_history_length: int = 2,
    ) -> None:
        self.owner = owner
        self.cpu_stats_history_length = cpu_stats_history_length

        self.last_stats: List[Dict[str, float]] = []
        self.save_cpu_snapshot()

        self.pod_cpu_limit = (
            float(pod_cpu_limit)
            if pod_cpu_limit and pod_cpu_limit != "unlimited"
            else None
        )

    @staticmethod
    def _get_cpu_time() -> Tuple[float, float]:
        user_time, system_time = os.times()[:2]
        return user_time, system_time

    def save_cpu_snapshot(self) -> None:
        user_time, system_time = self._get_cpu_time()
        real_time = time.time()

        self.last_stats.append(
            {
                "user_time": user_time,
                "system_time": system_time,
                "real_time": real_time,
            }
        )
        if len(self.last_stats) > self.cpu_stats_history_length:
            self.last_stats.pop(0)

    def get_cpu_usage(self) -> Optional[CpuData]:
        # The CPU usage is compared to the oldest snapshot in the list. If there are no snapshots, return None.
        if len(self.last_stats) <= 0:
            return None

        # Get current CPU and real time
        user_time, system_time = self._get_cpu_time()
        real_time = time.time()

        last_stats = self.last_stats[0]
        user_delta = user_time - last_stats["user_time"]
        system_delta = system_time - last_stats["system_time"]
        total_delta = user_delta + system_delta

        real_time_delta = real_time - last_stats["real_time"]
        cpu_percentage = (total_delta / real_time_delta) * 100

        limited_cpu = None
        if self.pod_cpu_limit:
            limited_cpu = cpu_percentage / self.pod_cpu_limit

        return CpuData(
            user_time=user_delta,
            system_time=system_delta,
            total_time=total_delta,
            elapsed_time=real_time_delta,
            cpu_percentage=cpu_percentage,
            limited_cpu=limited_cpu,
        )

    @staticmethod
    def get_memory_usage() -> Optional[MemoryData]:
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            return MemoryData(
                rss=mem_info.rss,
                vms=mem_info.vms,
                # Since both shared and dirty are not available on MacOS, we need to use getattr to access them without linter errors
                shared=getattr(mem_info, "shared", None),
                dirty=getattr(mem_info, "dirty", None),
            )
        except Exception:
            return None

    @staticmethod
    def get_thread_count() -> int:
        return threading.active_count()

    @staticmethod
    def get_gc_stats() -> List[Dict[str, int]]:
        return gc.get_stats()

    def monitor_process(self) -> Performance:
        cpu = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        thread_count = self.get_thread_count()
        gc_stats = self.get_gc_stats()

        return Performance(
            cpu=cpu,
            max_rss=memory_usage.rss if memory_usage else None,
            thread_count=thread_count,
            gc_stats=gc_stats,
            owner=self.owner,
        )
