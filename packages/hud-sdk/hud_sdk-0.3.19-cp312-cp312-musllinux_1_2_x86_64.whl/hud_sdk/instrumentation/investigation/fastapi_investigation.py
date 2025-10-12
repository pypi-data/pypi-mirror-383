import gzip
import json
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional, Union

from ...config import config
from ...flow_metrics import EndpointMetric
from ...investigation_manager import send_investigation_to_worker
from ...native import RawInvestigation
from ...schemas.investigation import ObservabilityIdentifiers
from ..limited_logger import limited_logger
from .http_investigation import (
    finish_base_http_investigation,
    safe_get_header,
)
from .investigation_utils import minimize_object_with_defaults

if TYPE_CHECKING:
    from starlette.datastructures import Headers


def bytes_to_generator(body: bytes) -> AsyncGenerator[bytes, None]:
    async def generator() -> AsyncGenerator[bytes, None]:
        yield body
        # The FormBody parser expect an empty body at the end so it will know the body is finished (not sure why the end of the iteration is not enough)
        yield b""

    return generator()


async def safe_parse_body(
    body: bytes, headers: Optional[Any], is_truncated: bool
) -> Union[Any, bytes]:
    # This functions is based on https://github.com/fastapi/fastapi/blob/97fdbdd0d8b3e24b3d850865033f6746ee13f82c/fastapi/routing.py#L242
    if is_truncated:
        return body

    try:
        if headers is None:
            return json.loads(body)

        headers = safe_parse_headers(headers)

        if headers is None:
            return json.loads(body)

        encoding = headers.get("content-encoding", "")
        if encoding == "gzip":
            try:
                body = gzip.decompress(body)
            except Exception:
                pass

        content_type = headers.get("content-type", "")
        if content_type == "application/json" or (
            content_type.startswith("application/") and content_type.endswith("+json")
        ):
            return json.loads(body)

        if "multipart/form-data" in content_type:
            from starlette.formparsers import MultiPartParser

            multipart_form_parser = MultiPartParser(headers, bytes_to_generator(body))
            result = dict(await multipart_form_parser.parse())
            parsed_result = {
                key: parse_mutipart_part(value) for key, value in result.items()
            }
            return parsed_result

        if content_type == "application/x-www-form-urlencoded":
            from starlette.formparsers import FormParser

            form_parser = FormParser(headers, bytes_to_generator(body))
            return dict(await form_parser.parse())

        return body
    except Exception as e:
        limited_logger.log(
            "Error parsing body",
            data={"error": str(e)},
        )
        return body


def parse_mutipart_part(value: Any) -> Any:
    from starlette.datastructures import UploadFile

    if isinstance(value, UploadFile):
        return {
            "filename": value.filename,
            "content_type": value.content_type,
            "file": value.file.read(config.investigation_max_string_length),
        }
    return value


def safe_parse_query_string(query_string: str) -> Dict[str, str]:
    try:
        from starlette.datastructures import QueryParams

        return dict(QueryParams(query_string))
    except Exception:
        return dict()


def safe_parse_headers(headers: Optional[Any]) -> Optional["Headers"]:
    try:
        from fastapi.datastructures import Headers

        if headers is None:
            return None

        return Headers(raw=headers)
    except Exception:
        return None


async def finish_fastapi_investigation(
    raw_investigation: RawInvestigation,
    metric: Optional[EndpointMetric],
    path: Optional[str],
    headers: Optional[Dict[str, str]],
    path_params: Optional[Dict[str, str]],
    query_string: Optional[str],
    raw_body: Optional[bytes],
    is_truncated: bool,
    apm_trace_ids: Optional[ObservabilityIdentifiers],
) -> None:
    investigation = finish_base_http_investigation(
        raw_investigation, metric, path, apm_trace_ids
    )

    if investigation is None:
        return

    parsed_body = (
        await safe_parse_body(raw_body, headers, is_truncated)
        if raw_body is not None
        else None
    )
    parsed_query_string = (
        safe_parse_query_string(query_string) if query_string is not None else None
    )

    investigation.context.request_body = minimize_object_with_defaults(parsed_body)
    investigation.context.query = minimize_object_with_defaults(parsed_query_string)
    investigation.context.params = minimize_object_with_defaults(path_params)

    headers_dict = safe_parse_headers(headers)
    investigation.context.content_type = safe_get_header(headers_dict, "content-type")
    investigation.context.content_encoding = safe_get_header(
        headers_dict, "content-encoding"
    )

    send_investigation_to_worker(investigation)
