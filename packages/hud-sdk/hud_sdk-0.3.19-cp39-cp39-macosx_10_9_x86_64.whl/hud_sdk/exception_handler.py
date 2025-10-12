import sys
from types import TracebackType
from typing import Any, Optional, Type

from .logging import internal_logger
from .utils import send_fatal_error

EXCEPTIONS_TO_IGNORE = [KeyboardInterrupt]


def install_exception_handler() -> None:
    ORIGINAL_EXCEPTHOOK = sys.excepthook

    def exception_handler(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
    ) -> Any:
        try:
            if exc_type not in EXCEPTIONS_TO_IGNORE:
                internal_logger.info(
                    "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
                )
                send_fatal_error(
                    exc_type, exc_value, exc_traceback, "Uncaught exception"
                )
        except Exception:
            internal_logger.warning("Failed to send fatal error", exc_info=True)
        finally:
            return ORIGINAL_EXCEPTHOOK(exc_type, exc_value, exc_traceback)

    sys.excepthook = exception_handler
