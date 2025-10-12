from typing import Any, Optional

from ...flow_metrics import ArqMetric
from ...investigation_manager import send_investigation_to_worker
from ...native import RawInvestigation
from ...schemas.investigation import ArqInvestigation, ArqInvestigationContext
from ..limited_logger import limited_logger
from .base_investigation import finish_base_investigation
from .investigation_utils import minimize_object_with_defaults


def finish_arq_investigation(
    raw_investigation: RawInvestigation,
    metric: Optional[ArqMetric],
    arq_function_name: str,
    arq_function_args: Optional[Any],
    arq_function_kwargs: Optional[Any],
    job_id: Optional[str],
    job_try: Optional[int],
) -> None:
    if metric is None:
        limited_logger.log("No metric when finishing arq investigation")
        return

    if metric.error is None:
        return

    investigation = finish_base_investigation(raw_investigation, metric)

    if investigation is None:
        return

    arq_investigation = ArqInvestigation(
        exceptions=investigation.exceptions,
        context=ArqInvestigationContext(
            timestamp=investigation.context.timestamp,
            machine_metrics=investigation.context.machine_metrics,
            system_info=investigation.context.system_info,
            arq_function_name=arq_function_name,
            arq_function_args=minimize_object_with_defaults(arq_function_args),
            arq_function_kwargs=minimize_object_with_defaults(arq_function_kwargs),
            job_id=job_id,
            job_try=job_try,
        ),
        flow_id=investigation.flow_uuid,
    )

    send_investigation_to_worker(arq_investigation)
