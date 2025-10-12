from typing import Any, Dict

from ..config import config
from ..logging import internal_logger


class LimitedLogger:
    def __init__(self, max_same_log: int):
        self._logged_logs: Dict[str, int] = dict()
        self._max_same_log = max_same_log

    def log(self, log_message: str, *args: Any, **kwargs: Any) -> None:
        self._logged_logs[log_message] = self._logged_logs.get(log_message, 0) + 1

        log_func = (
            internal_logger.debug
            if self._logged_logs[log_message] > self._max_same_log
            else internal_logger.warning
        )

        log_func(log_message, *args, **kwargs)


limited_logger = LimitedLogger(max_same_log=config.investigation_max_same_log)
