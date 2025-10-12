import json
from typing import TYPE_CHECKING

from ...flow_metrics import EndpointMetric
from ...instrumentation.apm_trace_ids import collect_apm_trace_ids
from ...instrumentation.investigation.http_investigation import (
    finish_base_http_investigation,
    safe_get_header,
)
from ...instrumentation.investigation.investigation_utils import (
    minimize_object_with_defaults,
)
from ...instrumentation.limited_logger import limited_logger
from ...investigation_manager import send_investigation_to_worker
from ...native import RawInvestigation

if TYPE_CHECKING:
    from django.http import HttpRequest


def finish_django_investigation(
    raw_investigation: RawInvestigation, metric: EndpointMetric, request: "HttpRequest"
) -> None:

    try:
        path_params = getattr(request, "resolver_match")
        if path_params:
            path_params = path_params.kwargs
    except Exception:
        path_params = None
        limited_logger.log(
            "Failed to get path params from request",
        )

    apm_traces = collect_apm_trace_ids(request.headers)

    investigation = finish_base_http_investigation(
        raw_investigation, metric, request.path, apm_traces
    )

    if investigation is None:
        return

    try:
        body = json.loads(request.body)
    except Exception:
        body = None
    investigation.context.request_body = minimize_object_with_defaults(body)
    investigation.context.query = minimize_object_with_defaults(request.GET)
    investigation.context.params = minimize_object_with_defaults(path_params)
    investigation.context.content_type = request.content_type
    investigation.context.content_encoding = safe_get_header(
        request.headers, "Content-Encoding"
    )

    send_investigation_to_worker(investigation)
