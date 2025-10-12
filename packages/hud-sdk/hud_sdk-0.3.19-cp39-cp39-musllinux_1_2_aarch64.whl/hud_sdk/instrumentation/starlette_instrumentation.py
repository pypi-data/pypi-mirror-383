from functools import wraps
from typing import TYPE_CHECKING, Any, Optional

from ..config import config
from ..flow_metrics import EndpointMetric
from ..logging import internal_logger
from ..native import RawInvestigation, begin_flow, set_investigation
from .apm_trace_ids import collect_apm_trace_ids
from .base_instrumentation import BaseInstrumentation
from .investigation.fastapi_investigation import (
    finish_fastapi_investigation,
    safe_parse_headers,
)
from .investigation.investigation_utils import open_investigation

if TYPE_CHECKING:
    from starlette.types import Message, Receive, Scope, Send


FLOW_ID_ATTR = "__hud_flow_id"


class StarletteInstrumentation(BaseInstrumentation):
    def __init__(self) -> None:
        super().__init__(
            "starlette", "starlette", "0.8.0", None
        )  # Minimum version that has ServerErrorMiddleware

    def is_enabled(self) -> bool:
        return config.instrument_fastapi

    def _instrument(self) -> None:
        import starlette.middleware.errors

        original_ServerErrorMiddleware_call = (
            starlette.middleware.errors.ServerErrorMiddleware.__call__
        )

        # We decided to monkey-patch ServerErrorMiddleware, since we needed not to change the original middleware stack for other instrumentation tools like OpenTelemetry,
        # which relies on the fact ServerErrorMiddleware is the last middleware in the stack and that it raises exceptions.
        # So we inherit from it, doing our logic on top of the original one and raising exceptions if needed.
        @wraps(original_ServerErrorMiddleware_call)
        async def __call__(
            self: Any, scope: "Scope", receive: "Receive", send: "Send"
        ) -> None:
            if scope.get("type") != "http":
                await original_ServerErrorMiddleware_call(self, scope, receive, send)
                return

            if scope.get("hud_running"):
                await original_ServerErrorMiddleware_call(self, scope, receive, send)
                return

            scope["hud_running"] = True
            metric: Optional[EndpointMetric] = None
            raw_investigation: Optional[RawInvestigation] = None
            try:
                begin_flow(None)
                metric = EndpointMetric()
                metric.start()
                raw_investigation = open_investigation()
            except Exception:
                internal_logger.exception("An error occurred in __call__")

            apm_trace_ids = None
            request_body = b""
            request_body_truncated = False

            def wrap_send(send: "Send") -> "Send":
                @wraps(send)
                async def wrapped_send(message: "Message") -> None:
                    try:
                        nonlocal metric, apm_trace_ids
                        if message.get("type") == "http.response.start":
                            status = message["status"]
                            if metric is not None:
                                metric.set_response_attributes(status)

                            # We handle the APM trace ids here since in the context we close the investigation the APM already removed their context
                            # For the same reason we do it before deduping
                            if status >= 500:
                                headers = safe_parse_headers(scope.get("headers"))
                                apm_trace_ids = collect_apm_trace_ids(
                                    dict(headers) if headers else None
                                )
                    except Exception:
                        internal_logger.exception(
                            "An error occurred in setting the response attributes"
                        )
                    await send(message)

                return wrapped_send

            def wrap_receive(receive: "Receive") -> "Receive":
                @wraps(receive)
                async def wrapped_receive() -> "Message":
                    nonlocal request_body, request_body_truncated
                    message = await receive()
                    try:
                        if message.get("type") == "http.request" and message.get(
                            "body"
                        ):
                            remain_bytes_length = (
                                config.investigation_max_body_length - len(request_body)
                            )

                            if remain_bytes_length > 0:
                                if remain_bytes_length < len(message["body"]):
                                    request_body_truncated = True

                                request_body += message["body"][:remain_bytes_length]
                            else:
                                request_body_truncated = True

                    except Exception:
                        pass

                    return message

                return wrapped_receive

            error = None
            try:
                await original_ServerErrorMiddleware_call(
                    self, scope, wrap_receive(receive), wrap_send(send)
                )
            except Exception as e:
                error = e

            try:
                if metric is not None:
                    metric.stop()
                route = scope.get("route")
                if not route:
                    path = scope.get("path", "")
                    internal_logger.warning(
                        "Cannot send endpoint metrics because route is not found",
                        data={"path": path},
                    )
                    set_investigation(
                        None
                    )  # Clear investigation in order to not gather more exceptions
                    return

                flow_id = getattr(route, FLOW_ID_ATTR, None)
                if metric is not None:
                    metric.flow_id = flow_id

                path = route.path
                method = scope.get("method", "")
                if path and method:
                    if metric is not None:
                        metric.set_request_attributes(path, method)

                    if raw_investigation is not None:
                        await finish_fastapi_investigation(
                            raw_investigation,
                            metric,
                            str(scope.get("path")),
                            scope.get("headers"),
                            scope.get("path_params"),
                            scope.get("query_string"),
                            request_body,
                            request_body_truncated,
                            apm_trace_ids,
                        )
                        set_investigation(None)
                    if metric is not None:
                        metric.save()
                else:
                    internal_logger.warning(
                        "Cannot send endpoint metrics because path or method is not found",
                        data={"path": path, "method": method},
                    )

            except Exception:
                internal_logger.exception(
                    "An error occurred in sending endpoint metrics"
                )

            finally:
                if error:
                    raise error

        starlette.middleware.errors.ServerErrorMiddleware.__call__ = __call__  # type: ignore[method-assign]
