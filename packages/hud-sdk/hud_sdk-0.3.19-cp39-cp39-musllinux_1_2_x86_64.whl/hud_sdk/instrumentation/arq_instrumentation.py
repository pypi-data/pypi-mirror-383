from functools import wraps
from typing import Any, Dict, TypedDict
from uuid import uuid4

from ..arq_declaration_manager import ArqDeclarationManager
from ..config import config
from ..flow_metrics import ArqMetric
from ..logging import internal_logger
from ..native import begin_flow, get_time, set_flow_id, set_investigation
from ..utils import mark_linked_function
from .base_instrumentation import BaseInstrumentation
from .investigation.arq_investigation import finish_arq_investigation
from .investigation.investigation_utils import open_investigation


class ArqInvestigationMetadata(TypedDict):
    arq_function_name: str
    arq_function_args: Any
    arq_function_kwargs: Any
    job_try: int


class ArqJobMetadata(TypedDict):
    metric: ArqMetric
    investigation_metadata: ArqInvestigationMetadata


class ArqInstrumentation(BaseInstrumentation):
    def __init__(self) -> None:
        super().__init__("arq", "arq", "0.26.0", None)
        self.arq_declaration_manager = ArqDeclarationManager()
        self.job_id_to_job_metadata = {}  # type: Dict[str, Dict[str, ArqJobMetadata]]

    def is_enabled(self) -> bool:
        return config.instrument_arq

    def _instrument(self) -> None:
        """
        Instrumentation summary:
        - Worker.__init__: Collect ArqFunction declarations and instrument the function to retrieve metric attributes
        - Worker.run_job: Enrich metric with start time and save it
        - deserialize_job_raw: The earliest function to know function_name to set flow id for a jon run
        """
        import arq

        internal_logger.info("Instrumenting arq")
        self._instrument_worker_init(arq)
        self._instrument_worker_run_job(arq)
        self._instrument_deserialize_job_raw(arq)

    def map_job_metadata_to_job_id(
        self, worker_id: str, job_id: str, job_metadata: ArqJobMetadata
    ) -> None:
        if worker_id not in self.job_id_to_job_metadata:
            self.job_id_to_job_metadata[worker_id] = {}
        if job_id not in self.job_id_to_job_metadata[worker_id]:
            self.job_id_to_job_metadata[worker_id][job_id] = job_metadata
        else:
            internal_logger.warning(
                "Metric already mapped to job id",
                data={
                    "job_id": job_id,
                    "existing_metric_flow_id": self.job_id_to_job_metadata[worker_id][
                        job_id
                    ]["metric"].flow_id,
                    "new_metric_flow_id": job_metadata["metric"].flow_id,
                },
            )

    def _instrument_worker_init(self, arq_module: Any) -> None:
        original_worker_init = arq_module.worker.Worker.__init__

        @wraps(original_worker_init)
        def _worker_init_wrapper(self_: Any, *args: Any, **kwargs: Any) -> Any:
            init_result = original_worker_init(self_, *args, **kwargs)

            try:
                if getattr(self_, "_HUD_wrapped_worker_id", None):
                    internal_logger.warning("Already instrumented arq.Worker.__init__")
                    return init_result

                worker_id = str(uuid4())
                setattr(self_, "_HUD_wrapped_worker_id", worker_id)

                functions = self_.functions

                for function_name, function_object in functions.items():
                    flow_id = self.arq_declaration_manager.save_arq_declaration(
                        function_name
                    )
                    self._instrument_coroutine(
                        flow_id, function_name, function_object, worker_id
                    )

                internal_logger.debug(
                    "Extracted and instrumented arq functions from worker",
                    data={"functions": len(functions)},
                )
            except Exception:
                internal_logger.exception(
                    "Error while iterating over arq functions from worker"
                )

            return init_result

        arq_module.worker.Worker.__init__ = _worker_init_wrapper
        internal_logger.debug("Instrumented worker.__init__")

    def _instrument_worker_run_job(self, arq_module: Any) -> None:
        original_worker_run_job = arq_module.worker.Worker.run_job

        @wraps(original_worker_run_job)
        async def _worker_run_job_wrapper(
            self_: Any, job_id: str, score: int, *args: Any, **kwargs: Any
        ) -> Any:
            start_time = None
            raw_investigation = None
            try:
                begin_flow()
                start_time = get_time()
                raw_investigation = open_investigation()
            except Exception:
                internal_logger.exception(
                    "Error while getting start time in arq.worker.run_job",
                    data={"job_id": job_id},
                )

            result = await original_worker_run_job(
                self_, job_id, score, *args, **kwargs
            )

            worker_id = getattr(self_, "_HUD_wrapped_worker_id", None)
            try:
                if not worker_id or worker_id not in self.job_id_to_job_metadata:
                    internal_logger.warning(
                        "Worker id attribute not found",
                        data={"job_id": job_id},
                    )
                    return result

                if (
                    not start_time
                    or job_id not in self.job_id_to_job_metadata[worker_id]
                ):
                    internal_logger.warning(
                        "Unable to set start time and save metric",
                        data={"job_id": job_id},
                    )
                    return result

                job_metadata = self.job_id_to_job_metadata[worker_id][job_id]
                metric = job_metadata["metric"]
                metric.set_start_time(start_time)
                metric.stop()
                metric.save()

                if raw_investigation:
                    investigation_metadata = job_metadata["investigation_metadata"]
                    finish_arq_investigation(
                        raw_investigation,
                        metric,
                        investigation_metadata["arq_function_name"],
                        investigation_metadata["arq_function_args"],
                        investigation_metadata["arq_function_kwargs"],
                        job_id,
                        investigation_metadata["job_try"],
                    )
                    set_investigation(None)

            except Exception:
                internal_logger.exception(
                    "Error while setting start time and saving metric in arq.worker.run_job",
                    data={"job_id": job_id},
                )
            finally:
                if (
                    worker_id
                    and worker_id in self.job_id_to_job_metadata
                    and job_id in self.job_id_to_job_metadata[worker_id]
                ):
                    del self.job_id_to_job_metadata[worker_id][job_id]

            return result

        arq_module.worker.Worker.run_job = _worker_run_job_wrapper
        internal_logger.debug("Instrumented worker.run_job")

    def _instrument_deserialize_job_raw(self, arq_module: Any) -> None:
        original_deserialize_job_raw = arq_module.worker.deserialize_job_raw

        @wraps(original_deserialize_job_raw)
        def _deserialize_job_raw_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = original_deserialize_job_raw(*args, **kwargs)

            try:
                function_name, *_ = result
                flow_id = self.arq_declaration_manager.get_arq_function_id(
                    function_name
                )
                set_flow_id(flow_id)
            except Exception:
                internal_logger.exception(
                    "Error while setting flow id", data={"function": function_name}
                )

            return result

        arq_module.worker.deserialize_job_raw = _deserialize_job_raw_wrapper
        internal_logger.debug("Instrumented deserialize_job_raw")

    def _instrument_coroutine(
        self, flow_id: str, function_name: str, arq_function: Any, worker_id: str
    ) -> None:
        """
        This function is called within existing try-catch context, so individual error handling is not needed here
        """
        mark_linked_function(arq_function.coroutine)
        original_coroutine = arq_function.coroutine

        if not callable(original_coroutine):
            internal_logger.warning(
                "Original coroutine is not callable", data={"function": function_name}
            )
            return

        if getattr(original_coroutine, "_HUD_wrapped", False):
            internal_logger.warning(
                "Original coroutine is already wrapped",
                data={"function": function_name},
            )
            return

        setattr(original_coroutine, "_HUD_wrapped", True)

        @wraps(original_coroutine)
        async def wrapped_coroutine(
            ctx: Dict[str, Any], *args: Any, **kwargs: Any
        ) -> Any:
            metric = None
            try:
                job_id = ctx.get("job_id")
                enqueue_time = ctx.get("enqueue_time")

                nonlocal flow_id
                set_flow_id(flow_id)
                metric = ArqMetric(flow_id)

                if enqueue_time:
                    metric.set_enqueue_time(enqueue_time.timestamp())

                if job_id:
                    job_metadata = ArqJobMetadata(
                        metric=metric,
                        investigation_metadata=ArqInvestigationMetadata(
                            arq_function_name=function_name,
                            arq_function_args=args,
                            arq_function_kwargs=kwargs,
                            job_try=ctx["job_try"],
                        ),
                    )

                    self.map_job_metadata_to_job_id(worker_id, job_id, job_metadata)
            except Exception:
                internal_logger.exception(
                    "Error while creating metric",
                    data={"function": function_name},
                )

            try:
                result = await original_coroutine(ctx, *args, **kwargs)
            except Exception as e:
                try:
                    if metric:
                        metric.set_error(e.__class__.__name__)
                except Exception:
                    internal_logger.exception(
                        "Error while setting error and mapping metric to job id",
                        data={"function": function_name},
                    )

                raise e

            return result

        arq_function.coroutine = wrapped_coroutine
