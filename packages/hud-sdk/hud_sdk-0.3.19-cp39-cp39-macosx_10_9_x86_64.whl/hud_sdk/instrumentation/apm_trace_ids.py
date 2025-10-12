import sys
from typing import Any, Mapping, Optional, Tuple

from ..schemas.investigation import B3Propagation, ObservabilityIdentifiers
from .investigation.http_investigation import safe_get_header
from .limited_logger import limited_logger


def safe_require(module_name: str) -> Optional[Any]:
    try:
        return sys.modules.get(module_name)
    except Exception:
        return None


def get_dd_trace_ids() -> Tuple[Optional[str], Optional[str]]:
    try:
        ddtrace = safe_require("ddtrace.trace")
        if ddtrace is None:
            return None, None

        context = ddtrace.tracer.current_trace_context()
        if context:
            return str(context.trace_id), str(context.span_id)
    except Exception as e:
        limited_logger.log("Failed to get ddtrace trace ids", data={"error": str(e)})

    return None, None


def get_otel_trace_id() -> Optional[str]:
    try:
        trace = safe_require("opentelemetry.trace")
        if trace is None:
            return None

        return str(trace.get_current_span().get_span_context().trace_id)
    except Exception as e:
        limited_logger.log(
            "Failed to get opentelemetry trace id", data={"error": str(e)}
        )

    return None


def get_b3_propagation(headers: Optional[Mapping[str, str]]) -> Optional[B3Propagation]:
    result = B3Propagation(
        full=safe_get_header(headers, "b3"),
        trace_id=safe_get_header(headers, "x-b3-traceid"),
        span_id=safe_get_header(headers, "x-b3-spanid"),
        parent_span_id=safe_get_header(headers, "x-b3-parentspanid"),
    )

    if (
        result.full is None
        and result.trace_id is None
        and result.span_id is None
        and result.parent_span_id is None
    ):
        return None

    return result


def collect_apm_trace_ids(
    headers: Optional[Mapping[str, str]],
) -> Optional[ObservabilityIdentifiers]:
    dd_trace_ids = get_dd_trace_ids()
    otel_trace_id = get_otel_trace_id()
    amazon_trace_id = safe_get_header(headers, "x-amzn-trace-id")
    w3c_baggage = safe_get_header(headers, "baggage")
    jaeger_trace_id = safe_get_header(headers, "uber-trace-id")
    b3_propagation = get_b3_propagation(headers)

    if amazon_trace_id is None and dd_trace_ids[0] is None and otel_trace_id is None:
        return None

    return ObservabilityIdentifiers(
        otel_trace_id=otel_trace_id,
        datadog_trace_id=dd_trace_ids[0],
        datadog_span_id=dd_trace_ids[1],
        amazon_trace_id=amazon_trace_id,
        w3c_baggage=w3c_baggage,
        jaeger_trace_id=jaeger_trace_id,
        b3_propagation=b3_propagation,
    )
