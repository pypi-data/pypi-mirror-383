import re
from typing import Any, Dict, List, Tuple, Union

from ..logging import internal_logger

# Across the file we use Any instead of re.Tupple since the type signature is changed across python versions

# Recursive type didn't work for me, so this type is mainly for documentation purposes and not enforcement
JsonableType = Union[
    int,
    float,
    bool,
    str,
    None,
    Dict[Any, Any],
    List[Any],
]


logged_once_per_type = set()


def log_once_per_type(obj_type: str) -> None:
    if obj_type in logged_once_per_type:
        return
    logged_once_per_type.add(obj_type)
    internal_logger.info(f"Failed to sensor object of type: {obj_type}")


def censor_object_in_place(
    obj: JsonableType,
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
) -> JsonableType:
    try:
        if isinstance(obj, str):
            for regex, replacement in regexes:
                obj = regex.sub(replacement, obj)
            return obj

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in black_list_params:
                    obj[key] = "[REDACTED]"
                    continue

                obj[key] = censor_object_in_place(value, regexes, black_list_params)
            return obj

        if isinstance(obj, list):
            return [
                censor_object_in_place(item, regexes, black_list_params) for item in obj
            ]

        if obj is None or isinstance(obj, (int, float, bool)):
            return obj

    except Exception:
        log_once_per_type(type(obj).__name__)
        return None

    # Drop anythig else including functions, Classes, etc
    return None


def censor_context(
    context: Dict[str, Any],
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
) -> Dict[str, Any]:
    if context["type"] == "http":
        return censor_http_context(context, regexes, black_list_params)
    elif context["type"] == "arq":
        return censor_arq_context(context, regexes, black_list_params)
    else:
        return context


def censor_base_context(
    context: Dict[str, Any],
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
) -> Dict[str, Any]:
    return {
        "type": context["type"],
        "timestamp": context["timestamp"],
        "machine_metrics": context["machine_metrics"],
        "system_info": context["system_info"],
    }


def censor_http_context(
    context: Dict[str, Any],
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
) -> Dict[str, Any]:
    return {
        **censor_base_context(context, regexes, black_list_params),
        "query": censor_object_in_place(context["query"], regexes, black_list_params),
        "params": censor_object_in_place(context["params"], regexes, black_list_params),
        "request_body": censor_object_in_place(
            context["request_body"], regexes, black_list_params
        ),
        "status_code": context["status_code"],
        "route": context["route"],
        "method": context["method"],
        "observability_identifiers": context["observability_identifiers"],
        "content_type": context.get("content_type"),
        "content_encoding": context.get("content_encoding"),
    }


def censor_arq_context(
    context: Dict[str, Any],
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
) -> Dict[str, Any]:
    return {
        **censor_base_context(context, regexes, black_list_params),
        "arq_function_name": context["arq_function_name"],
        "arq_function_args": censor_object_in_place(
            context["arq_function_args"], regexes, black_list_params
        ),
        "arq_function_kwargs": censor_object_in_place(
            context["arq_function_kwargs"], regexes, black_list_params
        ),
        "job_id": context["job_id"],
        "job_try": context["job_try"],
    }


def censor_exception_info(
    exception_info: Dict[str, Any],
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
) -> Dict[str, Any]:
    return {
        "name": exception_info["name"],
        "message": censor_object_in_place(
            exception_info["message"], regexes, black_list_params
        ),
        "stackTrace": exception_info["stackTrace"],
        "executionFlow": exception_info["executionFlow"],
    }


def censor_investigation(
    investigation: Dict[str, Any],
    regexes: List[Tuple[Any, str]],
    black_list_params: List[str],
    whitelist_nested_keys: List[str],
    blacklist_nested_keys: List[str],
) -> Dict[str, Any]:
    censored_investigation = {
        "exceptions": [
            censor_exception_info(exception_info, regexes, black_list_params)
            for exception_info in investigation["exceptions"]
        ],
        "context": censor_context(investigation["context"], regexes, black_list_params),
        "flow_type": investigation["flow_type"],
        "version": investigation["version"],
    }

    if len(whitelist_nested_keys) > 0:
        censored_investigation = pick_deep(
            censored_investigation, [key.split(".") for key in whitelist_nested_keys]
        )

    if len(blacklist_nested_keys) > 0:
        censored_investigation = omit_deep(
            censored_investigation, [key.split(".") for key in blacklist_nested_keys]
        )

    return censored_investigation


def create_censor_regexes(
    regexes: List[Tuple[str, str]],
) -> List[Tuple[Any, str]]:
    return [(re.compile(regex), replacement) for regex, replacement in regexes]


# Couldn't get the proper type to work...
def omit_deep(obj: Any, props: List[List[str]]) -> Any:
    if isinstance(obj, list):
        return [omit_deep(item, props) for item in obj]

    if not isinstance(obj, dict):
        return obj

    result = {**obj}
    for current_props in props:
        if len(current_props) == 0:
            continue

        current_key = current_props[0]
        if current_key not in result:
            continue

        if len(current_props) == 1:
            del result[current_key]
            continue

        result[current_key] = omit_deep(result[current_key], [current_props[1:]])

    return result


# Couldn't get the proper type to work...
def pick_deep(obj: Any, props: List[List[str]]) -> Any:
    if isinstance(obj, list):
        return [pick_deep(item, props) for item in obj]

    if not isinstance(obj, dict):
        return obj

    result = {}
    props_map: Dict[str, List[List[str]] | None] = {}

    for current_props in props:
        head, *rest = current_props
        props_map[head] = props_map.get(head, [])

        if rest and props_map[head] is not None:
            props_map[head].append(rest)  # type: ignore[union-attr]
            continue

        props_map[head] = None

    for key in props_map:
        if key not in obj:
            continue

        value = obj[key]
        if props_map[key] is None:
            result[key] = value
        elif isinstance(value, list):
            result[key] = [
                (
                    pick_deep(item, props_map[key])  # type: ignore[arg-type]
                    if isinstance(item, dict) or isinstance(item, list)
                    else {}
                )
                for item in value
            ]
        elif isinstance(value, dict):
            result[key] = pick_deep(value, props_map[key])  # type: ignore[arg-type]
    return result
