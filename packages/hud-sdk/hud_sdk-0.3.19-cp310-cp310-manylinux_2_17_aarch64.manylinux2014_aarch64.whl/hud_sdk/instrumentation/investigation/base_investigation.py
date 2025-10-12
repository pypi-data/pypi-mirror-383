from typing import Any, Optional

from ...config import config
from ...flow_metrics import FlowMetric
from ...native import RawInvestigation
from ...schemas.investigation import (
    BaseInvestigationContext,
    Investigation,
    InvestigationExceptionInfo,
)
from ..limited_logger import limited_logger
from .investigation_utils import (
    get_investigation_dedup,
    get_investigation_dedup_key,
    get_machine_metrics,
    get_system_info,
    get_total_investigations,
    increase_total_investigations,
    minimize_exception_info_in_place,
)


def finish_base_investigation(
    raw_investigation: RawInvestigation,
    metric: FlowMetric,
) -> Optional[Investigation[Any]]:
    if metric.flow_id is None:
        limited_logger.log("No flow id in metric")
        return None

    if raw_investigation.exceptions_count == 0:
        limited_logger.log("No exception in investigation")
        return None

    if raw_investigation.error_accoured == 1:
        limited_logger.log("Error accoured in investigation")
        return None

    if get_total_investigations() >= config.max_investigations:
        limited_logger.log("Max investigations reached")
        return None

    investigation_dedup = get_investigation_dedup()

    if investigation_dedup.get(metric.flow_id) is None:
        investigation_dedup[metric.flow_id] = dict()

    # Since python 3.7 dicts are ordered by default
    first_exception_key = next(iter(raw_investigation.exceptions), None)
    if first_exception_key is None:
        limited_logger.log("first exception key is None")
        return None

    first_exception = raw_investigation.exceptions[first_exception_key]
    key = get_investigation_dedup_key(first_exception)
    if investigation_dedup[metric.flow_id].get(key) is None:
        investigation_dedup[metric.flow_id][key] = 0

    if investigation_dedup[metric.flow_id][key] >= config.max_same_investigation:
        limited_logger.log("Max same investigation reached")
        return None

    increase_total_investigations()
    investigation_dedup[metric.flow_id][key] += 1

    return Investigation(
        exceptions=[
            minimize_exception_info_in_place(InvestigationExceptionInfo(raw_exception))
            for raw_exception in raw_investigation.exceptions.values()
        ],
        context=BaseInvestigationContext(
            type="base",
            timestamp=raw_investigation.start_time,
            machine_metrics=get_machine_metrics(),
            system_info=get_system_info(),
        ),
        flow_id=metric.flow_id,
    )
