from typing import Mapping, Optional

from ...flow_metrics import EndpointMetric
from ...native import RawInvestigation
from ...schemas.investigation import (
    HttpInvestigation,
    HttpInvestigationContext,
    ObservabilityIdentifiers,
)
from ..limited_logger import limited_logger
from .base_investigation import finish_base_investigation


def finish_base_http_investigation(
    raw_investigation: RawInvestigation,
    metric: Optional[EndpointMetric],
    path: Optional[str],
    apm_trace_ids: Optional[ObservabilityIdentifiers],
) -> Optional[HttpInvestigation]:
    if metric is None:
        limited_logger.log("No metric when finishing http investigation")
        return None

    if metric.status_code is None:
        return None

    if metric.status_code < 500:
        return None

    investigation = finish_base_investigation(raw_investigation, metric)

    if investigation is None:
        return None

    return HttpInvestigation(
        exceptions=investigation.exceptions,
        context=HttpInvestigationContext(
            status_code=metric.status_code,
            route=path or "unknown",
            method=metric.method or "unknown",
            timestamp=investigation.context.timestamp,
            query_params=None,
            path_params=None,
            body=None,
            observability_identifiers=apm_trace_ids,
            content_type=None,
            content_encoding=None,
            machine_metrics=investigation.context.machine_metrics,
            system_info=investigation.context.system_info,
        ),
        flow_id=investigation.flow_uuid,
    )


def safe_get_header(
    headers: Optional[Mapping[str, str]], header_name: str
) -> Optional[str]:
    try:
        if headers is None:
            return None

        return headers.get(header_name)
    except Exception as e:
        limited_logger.log(
            "Failed to get header", data={"error": str(e), "header_name": header_name}
        )
    return None
