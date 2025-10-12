import os
import shutil
import sys
import time
from functools import wraps
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Coroutine, Optional, Type, TypeVar, Union
from uuid import UUID, uuid5

from .client import get_client
from .config import config
from .logging import internal_logger, send_logs_handler
from .native import check_linked_code, mark_linked_code
from .process_utils import get_current_pid
from .schemas.requests import FatalError, SessionlessLogs
from .user_options import get_user_options
from .version import version

T = TypeVar("T")


def suppress_exceptions_async(
    default_return_factory: Callable[[], T],
) -> Callable[
    [Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]
]:
    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception:
                internal_logger.exception(
                    "Exception in {}".format(getattr(func, "__name__", None))
                )
                return default_return_factory()

        return async_wrapper

    return decorator


def suppress_exceptions_sync(
    default_return_factory: Callable[[], T],
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception:
                internal_logger.exception(
                    "Suppressed exception in function",
                    data={"function": getattr(func, "__name__", None)},
                )
                return default_return_factory()

        return sync_wrapper

    return decorator


def mark_linked_function(function: Callable[..., Any]) -> None:
    if hasattr(function, "__code__"):
        if not check_linked_code(function.__code__):
            mark_linked_code(function.__code__)
    elif hasattr(function, "__call__") and hasattr(function.__call__, "__code__"):
        if not check_linked_code(function.__call__.__code__):
            mark_linked_code(function.__call__.__code__)
    else:
        name = getattr(function, "__name__", None)
        internal_logger.warning("Could not mark linked code", data={"function": name})


def calculate_uuid(unique_str: str) -> UUID:
    return uuid5(config.uuid_namespace, unique_str)


def send_fatal_error(
    exc_type: Optional[Type[BaseException]] = None,
    exc_value: Optional[BaseException] = None,
    exc_traceback: Optional[TracebackType] = None,
    message: Optional[str] = None,
) -> None:
    client = None
    try:
        if exc_type is None and exc_value is None and exc_traceback is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()

        client = get_client(is_async=False, user_identity=get_user_options())
        fatal_error = FatalError.FatalErrorData(
            exc_type=exc_type,
            exc_value=exc_value,
            exc_traceback=exc_traceback,
            pid=get_current_pid(),
            extra_message=message,
        )
        client.send_fatal_error(fatal_error)
    except Exception:
        pass
    finally:
        if client:
            client.close()


def dump_logs_sync(session_id: Optional[str]) -> None:
    client = None
    try:
        user_options = get_user_options()
        client = get_client(is_async=False, user_identity=user_options)
        logs = send_logs_handler.get_and_clear_logs()
        if session_id:
            client.set_session_id(session_id)
            client.send_logs_json(logs.to_dict(), "Logs")
        else:
            if (
                user_options is None
                or user_options.key is None
                or user_options.service is None
            ):
                return
            sessionless_logs = SessionlessLogs(
                logs,
                user_options.key,
                user_options.service,
                user_options.tags,
                version,
                None,
            )
            client.send_sessionless_logs_json(
                sessionless_logs.to_dict(), "SessionlessLogs"
            )
    except Exception:
        pass
    finally:
        if client:
            client.close()


def is_uwsgi() -> bool:
    try:
        import uwsgi  # noqa: F401

        return True
    except ImportError:
        return False


def _find_python_from_sdk_directory() -> Optional[str]:
    current_file_path = Path(__file__)
    while current_file_path.name != "site-packages":
        current_file_path = current_file_path.parent
        if current_file_path == current_file_path.parent:
            internal_logger.warning(
                "Could not find site-packages directory",
                data={
                    "file": __file__,
                },
            )
            break

    python_path = str(current_file_path.parent).replace("lib", "bin")
    if (
        os.path.exists(python_path)
        and os.path.isfile(python_path)
        and os.access(python_path, os.X_OK)
    ):
        internal_logger.info(
            "Python binary found from the directory as the SDK",
            data={"python_path": python_path},
        )
        return python_path

    return None


def _find_python_in_site_packages() -> Optional[str]:
    for path in sys.path:
        if "site-packages" == Path(path).name:
            python_path = (
                Path(path).resolve().parent
            )  # .../pythonX.Y/site-packages -> .../pythonX.Y

            python_bin_path = str(python_path).replace("lib", "bin")
            python_name = python_bin_path.split("/")[-1]
            python_version = python_name.split("python")[1].split(".")
            if (
                str(sys.version_info.major) != python_version[0]
                or str(sys.version_info.minor) != python_version[1]
            ):
                internal_logger.warning(
                    "Python binary version mismatch",
                    data={
                        "python_version": python_version,
                        "python_major": str(sys.version_info.major),
                        "python_minor": str(sys.version_info.minor),
                    },
                )
                continue
            if (
                os.path.exists(python_bin_path)
                and os.path.isfile(python_bin_path)
                and os.access(python_bin_path, os.X_OK)
            ):
                internal_logger.info(
                    "Python binary found in site-packages",
                    data={"python_path": python_bin_path},
                )
                return python_bin_path
    return None


def find_python_binary() -> Optional[str]:
    if "python" in Path(sys.executable).name:
        internal_logger.info(
            "Using python binary from sys.executable",
            data={"sys_executable": sys.executable},
        )
        return sys.executable
    if not is_uwsgi():
        internal_logger.warning(
            "Unkown sys.executable", data={"sys_executable": sys.executable}
        )
        return None

    internal_logger.info("uwsgi found")
    if config.python_binary:
        internal_logger.info(
            "Python binary found in config",
            data={"python_binary": config.python_binary},
        )
        return config.python_binary

    python_path = _find_python_from_sdk_directory()
    if python_path:
        return python_path

    python_path = _find_python_in_site_packages()
    if python_path:
        return python_path

    current_python_name = "python{}.{}".format(
        str(sys.version_info.major), str(sys.version_info.minor)
    )
    python_path = shutil.which(current_python_name)
    if python_path:
        internal_logger.info(
            "Python binary found in using shutil.which",
            data={"python_path": python_path},
        )
        return python_path

    return python_path


def get_time_since_epoch_in_ns() -> int:
    if hasattr(time, "time_ns"):
        return time.time_ns()
    return int(time.time() * 1e9)


def timestamp_to_ns(timestamp: Union[int, float]) -> int:
    """
    Converts a numeric timestamp into nanoseconds.
    """
    if timestamp < 1e10:  # Likely seconds
        return int(timestamp * 1e9)
    elif timestamp < 1e13:  # Likely milliseconds
        return int(timestamp * 1e6)
    elif timestamp < 1e16:  # Likely microseconds
        return int(timestamp * 1e3)
    else:
        # Likely nanoseconds
        return int(timestamp)
