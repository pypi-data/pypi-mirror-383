import sys
import traceback
from typing import Any, Dict, Generic, List, Optional, TypeVar

from hud_sdk.native import RawExceptionExecution

from .events import CpuData, MemoryData
from .schema import Schema


class B3Propagation(Schema):
    def __init__(
        self,
        full: Optional[str],
        trace_id: Optional[str],
        span_id: Optional[str],
        parent_span_id: Optional[str],
    ):
        self.full = full
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id

    def to_dict(self) -> Dict[str, Any]:

        return {
            "full": self.full,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
        }


class ObservabilityIdentifiers(Schema):
    def __init__(
        self,
        otel_trace_id: Optional[str],
        datadog_trace_id: Optional[str],
        datadog_span_id: Optional[str],
        amazon_trace_id: Optional[str],
        w3c_baggage: Optional[str],
        jaeger_trace_id: Optional[str],
        b3_propagation: Optional[B3Propagation],
    ):
        self.otel_trace_id = otel_trace_id
        self.datadog_trace_id = datadog_trace_id
        self.datadog_span_id = datadog_span_id
        self.amazon_trace_id = amazon_trace_id
        self.w3c_baggage = w3c_baggage
        self.jaeger_trace_id = jaeger_trace_id
        self.b3_propagation = b3_propagation

    def to_dict(self) -> Dict[str, Any]:

        return {
            "otel_trace_id": self.otel_trace_id,
            "datadog_trace_id": self.datadog_trace_id,
            "datadog_span_id": self.datadog_span_id,
            "amazon_trace_id": self.amazon_trace_id,
            "w3c_baggage": self.w3c_baggage,
            "jaeger_trace_id": self.jaeger_trace_id,
            "b3_propagation": (
                self.b3_propagation.to_dict() if self.b3_propagation else None
            ),
        }


class MachineMetrics(Schema):
    def __init__(
        self, cpu: Optional[CpuData], memory: Optional[MemoryData], threads_count: int
    ):
        self.cpu = cpu
        self.memory = memory
        self.threads_count = threads_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu": self.cpu.to_dict() if self.cpu else None,
            "memory": self.memory.to_dict() if self.memory else None,
            "threads_count": self.threads_count,
        }


class SystemInfo(Schema):
    def __init__(
        self,
        pod_name: Optional[str],
        node_name: Optional[str],
    ):
        self.pod_name = pod_name
        self.node_name = node_name
        self.python_version = sys.version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pod_name": self.pod_name,
            "node_name": self.node_name,
            "python_version": self.python_version,
        }


C = TypeVar("C", bound="BaseInvestigationContext")


class BaseInvestigationContext(Schema):
    def __init__(
        self,
        type: str,
        timestamp: int,
        machine_metrics: Optional[MachineMetrics],
        system_info: Optional[SystemInfo],
    ):
        self.type = type
        self.timestamp = timestamp
        self.machine_metrics = machine_metrics
        self.system_info = system_info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "machine_metrics": (
                self.machine_metrics.to_dict() if self.machine_metrics else None
            ),
            "system_info": self.system_info.to_dict() if self.system_info else None,
        }


class HttpInvestigationContext(BaseInvestigationContext):
    def __init__(
        self,
        timestamp: int,
        machine_metrics: Optional[MachineMetrics],
        system_info: Optional[SystemInfo],
        status_code: int,
        route: str,
        method: str,
        query_params: Optional[Any],
        path_params: Optional[Any],
        body: Optional[Any],
        observability_identifiers: Optional[ObservabilityIdentifiers],
        content_type: Optional[str],
        content_encoding: Optional[str],
    ):
        super().__init__("http", timestamp, machine_metrics, system_info)
        self.observability_identifiers = observability_identifiers
        self.method = method
        self.params = path_params
        self.query = query_params
        self.request_body = body
        self.route = route
        self.status_code = status_code
        self.content_type = content_type
        self.content_encoding = content_encoding

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "request_body": self.request_body,
            "query": self.query,
            "params": self.params,
            "status_code": self.status_code,
            "route": self.route,
            "method": self.method,
            "observability_identifiers": (
                self.observability_identifiers.to_dict()
                if self.observability_identifiers
                else None
            ),
            "content_type": self.content_type,
            "content_encoding": self.content_encoding,
        }


class ArqInvestigationContext(BaseInvestigationContext):
    def __init__(
        self,
        timestamp: int,
        machine_metrics: Optional[MachineMetrics],
        system_info: Optional[SystemInfo],
        arq_function_name: str,
        arq_function_args: Optional[Any],
        arq_function_kwargs: Optional[Any],
        job_id: Optional[str],
        job_try: Optional[int],
    ):
        super().__init__("arq", timestamp, machine_metrics, system_info)
        # Context does not include observability_identifiers because other APM tools don't support arq
        self.arq_function_name = arq_function_name
        self.arq_function_args = arq_function_args
        self.arq_function_kwargs = arq_function_kwargs
        self.job_id = job_id
        self.job_try = job_try

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "arq_function_name": self.arq_function_name,
            "arq_function_args": self.arq_function_args,
            "arq_function_kwargs": self.arq_function_kwargs,
            "job_id": self.job_id,
            "job_try": self.job_try,
        }


def get_exception_stack_trace(exception: Exception) -> str:
    if sys.version_info.minor <= 9:
        return "".join(
            traceback.format_exception(
                exception.__class__, exception, exception.__traceback__
            )
        )

    return "".join(traceback.format_exception(exception))


class ExecutionFlowItem(Schema):
    def __init__(self, function_id: str, caller_function_id: str):
        self.function_id = function_id
        self.caller_function_id = caller_function_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function_id": self.function_id,
            "caller_function_id": self.caller_function_id,
        }


def safe_str(obj: Any) -> str:
    try:
        return str(obj)
    except Exception:
        return "FAILED_TO_SERIALIZE"


class InvestigationExceptionInfo(Schema):
    def __init__(self, raw_exception: RawExceptionExecution):
        self.name = raw_exception.name
        self.message = (
            safe_str(raw_exception.exception_args[0])
            if raw_exception.exception_args is not None
            and len(raw_exception.exception_args) == 1
            else safe_str(raw_exception.exception_args)
        )
        self.stack_trace = self._prepare_stack_trace(raw_exception)
        self.execution_flow = [
            ExecutionFlowItem(item[0], item[1]) for item in raw_exception.execution_flow
        ]

    def _prepare_stack_trace(self, exception: RawExceptionExecution) -> str:
        stack_trace = ""
        if exception.exception_tracebacks is not None:
            for trace in reversed(exception.exception_tracebacks):
                stack_trace += f"{trace[0]}:{trace[1]}:{trace[2]}\n"

        if exception.exception_frames is not None:
            for frame in exception.exception_frames:
                stack_trace += f"{frame[0]}:{frame[1]}:{frame[2]}\n"

        return stack_trace[:-1]  # remove the last newline

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "stackTrace": self.stack_trace,
            "executionFlow": [item.to_dict() for item in self.execution_flow],
        }


class Investigation(Schema, Generic[C]):
    def __init__(
        self,
        exceptions: List[InvestigationExceptionInfo],
        context: C,
        flow_id: str,
    ):
        self.exceptions = exceptions
        self.context = context
        self.flow_type = context.type
        self.flow_uuid = flow_id
        self.version = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exceptions": [exception.to_dict() for exception in self.exceptions],
            "context": self.context.to_dict(),
            "flow_type": self.flow_type,
            "flow_uuid": self.flow_uuid,
            "version": self.version,
        }


class HttpInvestigation(Investigation[HttpInvestigationContext]):
    pass


class ArqInvestigation(Investigation[ArqInvestigationContext]):
    pass
