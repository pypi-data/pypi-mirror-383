import traceback
from datetime import datetime
from types import TracebackType
from typing import Any, Dict, List, Optional, Type

from .events import FileDeclaration, Log
from .schema import Schema


class Init(Schema):
    def __init__(
        self,
        sdk_version: str,
        service: str,
        start_time: datetime,
        token: str,
        type: str,
        tags: Dict[str, str],
        exporter_run_id: str,
    ):
        self.sdk_version = sdk_version
        self.service = service
        self.start_time = start_time
        self.token = token
        self.type = type
        self.version = "1.0.0"
        self.tags = tags
        self.exporter_run_id = exporter_run_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sdk_version": self.sdk_version,
            "service": self.service,
            "start_time": self.start_time.isoformat(),
            "token": self.token,
            "type": self.type,
            "version": self.version,
            "tags": self.tags,
            "exporter_run_id": self.exporter_run_id,
        }


class Send(Schema):
    def __init__(
        self,
        event_version: str,
        raw: Any,
        send_time: datetime,
        source: str,
        type: str,
    ):
        self.event_version = event_version
        self.raw = raw
        self.send_time = send_time
        self.source = source
        self.type = type
        self.version = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_version": self.event_version,
            "raw": self.raw,
            "send_time": self.send_time.isoformat(),
            "source": self.source,
            "type": self.type,
            "version": self.version,
        }


class Batch(Schema):
    def __init__(
        self,
        arr: List[Any],
        event_version: str,
        send_time: datetime,
        source: str,
        type: str,
    ):
        self.arr = arr
        self.event_version = event_version
        self.send_time = send_time
        self.source = source
        self.type = type
        self.version = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arr": self.arr,
            "event_version": self.event_version,
            "send_time": self.send_time.isoformat(),
            "source": self.source,
            "type": self.type,
            "version": self.version,
        }


class Logs(Schema):
    def __init__(
        self,
        logs: List[Log],
        send_time: datetime,
    ):
        self.logs = logs
        self.send_time = send_time

    def to_dict(self) -> Dict[str, Any]:
        from ..json import dumps

        logs = []  # type: List[str]
        for log in self.logs:
            try:
                logs.append(dumps(log.to_dict()).decode("utf-8"))
            except Exception:
                logs.append(
                    dumps(
                        Log(
                            "Failed to serialize log",
                            {
                                "exception": traceback.format_exc(),
                                "original_message": log.message,
                            },
                            log.timestamp,
                            "ERROR",
                            log.pathname,
                            log.lineno,
                        ).to_dict()
                    ).decode("utf-8")
                )
        return {
            "logs": "\n".join(logs),
            "send_time": self.send_time.isoformat(),
        }


class SessionlessLogs(Schema):
    def __init__(
        self,
        logs_request: Logs,
        token: str,
        service: Optional[str],
        tags: Dict[str, str],
        sdk_version: str,
        exporter_run_id: Optional[str],
    ):
        self.logs_request = logs_request
        self.token = token
        self.service = service
        self.tags = tags
        self.sdk_version = sdk_version
        self.exporter_run_id = exporter_run_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.logs_request.to_dict(),
            "token": self.token,
            "service": self.service,
            "tags": self.tags,
            "sdk_version": self.sdk_version,
            "exporter_run_id": self.exporter_run_id,
        }


class FatalError(Schema):

    class FatalErrorData:
        def __init__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            exc_traceback: Optional[TracebackType],
            pid: int,
            extra_message: Optional[str] = None,
        ):
            self.error_message = str(exc_value) if exc_value else ""
            self.error_name = exc_type.__name__ if exc_type else ""
            self.error_stack = (
                "".join(traceback.format_tb(exc_traceback)) if exc_traceback else ""
            )
            self.pid = pid
            self.extra_message = extra_message

    def __init__(
        self,
        fatal_error: FatalErrorData,
        send_time: datetime,
        token: Optional[str] = None,
        service: Optional[str] = None,
    ):
        self.error_message = fatal_error.error_message
        self.error_name = fatal_error.error_name
        self.error_stack = fatal_error.error_stack
        self.pid = fatal_error.pid
        self.extra_message = fatal_error.extra_message
        self.send_time = send_time
        self.token = token
        self.service = service

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_message": self.error_message,
            "error_name": self.error_name,
            "error_stack": self.error_stack,
            "pid": self.pid,
            "extra_message": self.extra_message,
            "send_time": self.send_time.isoformat(),
            "token": self.token,
            "service": self.service,
        }


class FileDeclarations(Schema):
    def __init__(
        self,
        files: List[FileDeclaration],
    ):
        self.files = files

    def to_dict(self) -> Dict[str, Any]:
        return {"files": [file.to_dict() for file in self.files]}


class Ping(Schema):
    def __init__(
        self,
        send_time: datetime,
    ):
        self.send_time = send_time
        self.extra: Dict[None, None] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "send_time": self.send_time.isoformat(),
            "extra": self.extra,
        }
