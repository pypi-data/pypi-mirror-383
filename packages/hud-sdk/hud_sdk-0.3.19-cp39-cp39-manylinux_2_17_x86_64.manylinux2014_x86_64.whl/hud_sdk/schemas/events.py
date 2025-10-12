from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..format_utils import format_path_declaration
from ..process_utils import get_current_pid
from .schema import JSON, Schema

CallersType = Tuple[Optional[Tuple[str, str, int, bool]], ...]


class Event(Schema):
    @classmethod
    @abstractmethod
    def get_version(cls) -> str: ...

    @classmethod
    def get_type(cls) -> str:
        return cls.__name__


class EventWithPid(Event):
    def to_dict(self) -> Dict[str, Any]:
        """Create dictionary directly with PID injection for maximum efficiency"""
        data = super().to_dict()
        if "pid" not in data:
            data["pid"] = get_current_pid()
        return data


class ArgumentType(Enum):
    POSITIONAL_ONLY = "positional_only"
    ARG = "arg"
    VARARG = "vararg"
    KEYWORD_ONLY = "keyword_only"
    KWARG = "kwarg"


class FunctionArgument(Schema):
    def __init__(self, name: str, _type: ArgumentType):
        self.name = name
        self.type = _type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
        }


class CodeBlockType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"


class ScopeType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"


class ScopeNode(Schema):
    def __init__(self, type: ScopeType, name: str):
        self.type = type
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "name": self.name,
        }

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ScopeNode):
            return False
        return self.type == other.type and self.name == other.name


class FunctionDeclaration(Event):
    def __init__(
        self,
        file: str,
        function_id: str,
        is_async: bool,
        name: str,
        source_code_hash: str,
        start_line: int,
        end_line: Optional[int],
        code_block_type: CodeBlockType,
        file_checksum: int,
        declarations_count: int,
        arguments: Optional[List[FunctionArgument]] = None,
        scope: Optional[List[ScopeNode]] = None,
    ):
        self.file = file
        self.function_id = function_id
        self.is_async = is_async
        self.name = name
        self.source_code_hash = source_code_hash
        self.start_line = start_line
        self.end_line = end_line
        self.code_block_type = code_block_type
        self.file_checksum = file_checksum
        self.declarations_count = declarations_count
        self.arguments = arguments or []
        self.scope = scope or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "function_id": self.function_id,
            "is_async": self.is_async,
            "name": self.name,
            "source_code_hash": self.source_code_hash,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "code_block_type": self.code_block_type.value,
            "file_checksum": self.file_checksum,
            "declarations_count": self.declarations_count,
            "arguments": [arg.to_dict() for arg in self.arguments],
            "scope": [scope.to_dict() for scope in self.scope],
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.1"


class Sketch(Schema):
    def __init__(self, bin_width: float, index_shift: int, data: List[int]):
        self.bin_width = bin_width
        self.index_shift = index_shift
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bin_width": self.bin_width,
            "index_shift": self.index_shift,
            "data": self.data,
        }


class Invocations(EventWithPid):
    def __init__(
        self,
        count: int,
        function_id: str,
        sampled_count: int,
        sum_duration: int,
        sum_squared_duration: int,
        timeslice: int,
        timestamp: datetime,
        caller: Optional[str],
        exceptions: Dict[str, int],
        sketch: Sketch,
        wrapped_flow_id: Optional[str],
        is_linked_function: bool,
    ):
        self.count = count
        self.function_id = function_id
        self.sampled_count = sampled_count
        self.sum_duration = sum_duration
        self.sum_squared_duration = sum_squared_duration
        self.timeslice = timeslice
        self.timestamp = timestamp
        self.caller = caller
        self.exceptions = exceptions
        self.sketch = sketch
        self.wrapped_flow_id = wrapped_flow_id
        self.is_linked_function = is_linked_function

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "count": self.count,
            "function_id": self.function_id,
            "sampled_count": self.sampled_count,
            "sum_duration": self.sum_duration,
            "sum_squared_duration": self.sum_squared_duration,
            "timeslice": self.timeslice,
            "timestamp": self.timestamp.isoformat(),
            "caller": self.caller,
            "wrapped_flow_id": self.wrapped_flow_id,
            "exceptions": self.exceptions,
            "sketch": self.sketch.to_dict(),
            "is_linked_function": self.is_linked_function,
        }
        return result

    @classmethod
    def get_version(cls) -> str:
        return "1.0.2"


class AwsWorkloadData(Schema):
    def __init__(
        self,
        ami_id: str,
        launched_date: str,
        life_cycle: str,
        region: str,
        workload_id: str,
        workload_instance_type: str,
    ):
        self.ami_id = ami_id
        self.launched_date = launched_date
        self.life_cycle = life_cycle
        self.region = region
        self.workload_id = workload_id
        self.workload_instance_type = workload_instance_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ami_id": self.ami_id,
            "launched_date": self.launched_date,
            "life_cycle": self.life_cycle,
            "region": self.region,
            "workload_id": self.workload_id,
            "workload_instance_type": self.workload_instance_type,
        }


class KubernetesWorkloadData(Schema):
    def __init__(
        self,
        pod_name: str,
        pod_cpu_limit: Optional[str],
        pod_memory_limit: Optional[int],
        pod_namespace: Optional[str],
        product_uuid: Optional[str],
    ):
        self.pod_name = pod_name
        self.pod_cpu_limit = pod_cpu_limit
        self.pod_memory_limit = pod_memory_limit
        self.pod_namespace = pod_namespace
        self.product_uuid = product_uuid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pod_name": self.pod_name,
            "pod_cpu_limit": self.pod_cpu_limit,
            "pod_memory_limit": self.pod_memory_limit,
            "pod_namespace": self.pod_namespace,
            "product_uuid": self.product_uuid,
        }


class WorkloadData(Event):
    def __init__(
        self,
        aws_workload_data: Optional[AwsWorkloadData] = None,
        kubernetes_workload_data: Optional[KubernetesWorkloadData] = None,
    ):
        self.aws_workload_data = aws_workload_data
        self.kubernetes_workload_data = kubernetes_workload_data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aws_workload_data": (
                self.aws_workload_data.to_dict() if self.aws_workload_data else None
            ),
            "kubernetes_workload_data": (
                self.kubernetes_workload_data.to_dict()
                if self.kubernetes_workload_data
                else None
            ),
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class LogExceptionInfo(Schema):
    def __init__(self, name: str, value: str, stack_trace: str):
        self.name = name
        self.value = value
        self.stack_trace = stack_trace

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "stack_trace": self.stack_trace,
        }


class Log(EventWithPid):
    def __init__(
        self,
        message: str,
        data: Dict[str, Any],
        timestamp: float,
        level: str,
        pathname: str,
        lineno: int,
        exception: Optional[LogExceptionInfo] = None,
    ):
        self.message = message
        self.data = data
        self.timestamp = timestamp
        self.level = level
        self.pathname = pathname
        self.lineno = lineno
        self.exc = exception

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
            "level": self.level,
            "pathname": self.pathname,
            "lineno": self.lineno,
            "exc": self.exc.to_dict() if self.exc else None,
        }
        return result

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class CpuData(Schema):
    def __init__(
        self,
        user_time: float,
        system_time: float,
        total_time: float,
        elapsed_time: float,
        cpu_percentage: float,
        limited_cpu: Optional[float] = None,
    ):
        self.user_time = user_time
        self.system_time = system_time
        self.total_time = total_time
        self.elapsed_time = elapsed_time
        self.cpu_percentage = cpu_percentage
        self.limited_cpu = limited_cpu

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_time": self.user_time,
            "system_time": self.system_time,
            "elapsed_time": self.elapsed_time,
            "cpu_percentage": self.cpu_percentage,
            "limited_cpu": self.limited_cpu,
            "total_time": self.total_time,
        }


class MemoryData(Schema):
    def __init__(
        self,
        rss: int,
        vms: int,
        shared: Optional[int],
        dirty: Optional[int],
    ):
        self.rss = rss
        self.vms = vms
        self.shared = shared
        self.dirty = dirty

    def to_dict(self) -> Dict[str, Any]:

        return {
            "rss": self.rss,
            "vms": self.vms,
            "shared": self.shared,
            "dirty": self.dirty,
        }


class Performance(EventWithPid):
    def __init__(
        self,
        cpu: Optional[CpuData],
        max_rss: Optional[int],
        thread_count: int,
        gc_stats: List[Dict[str, int]],
        owner: str,
    ):
        self.cpu = cpu
        self.max_rss = max_rss
        self.thread_count = thread_count
        self.gc_stats = gc_stats
        self.owner = owner

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "cpu": self.cpu.to_dict() if self.cpu else None,
            "max_rss": self.max_rss,
            "thread_count": self.thread_count,
            "gc_stats": self.gc_stats,
            "owner": self.owner,
        }
        return result

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class Runtime(Event):
    def __init__(
        self,
        python_version: str,
        platform_info: str,
        architecture: str,
        pid: int,
        cwd: str,
        exec_path: str,
        argv: List[str],
    ):
        self.python_version = python_version
        self.platform_info = platform_info
        self.architecture = architecture
        self.pid = pid
        self.cwd = cwd
        self.exec_path = exec_path
        self.argv = argv

    def to_dict(self) -> Dict[str, Any]:
        return {
            "python_version": self.python_version,
            "platform_info": self.platform_info,
            "architecture": self.architecture,
            "pid": self.pid,
            "cwd": self.cwd,
            "exec_path": self.exec_path,
            "argv": self.argv,
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class ModuleData(Schema):
    def __init__(self, name: str, version: Optional[str]):
        self.name = name
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
        }


class LoadedModules(EventWithPid):
    def __init__(self, modules: List[ModuleData]):
        self.modules = modules

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modules": [module.to_dict() for module in self.modules],
            "pid": get_current_pid(),
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class PreInitLoadedModules(EventWithPid):
    def __init__(self, modules: List[ModuleData]):
        self.modules = modules

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modules": [module.to_dict() for module in self.modules],
            "pid": get_current_pid(),
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class InstalledPackages(Event):
    def __init__(self, modules: List[ModuleData]):
        self.modules = modules

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modules": [module.to_dict() for module in self.modules],
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class EndpointDeclaration(Event):
    def __init__(self, flow_id: str, path: str, methods: List[str], framework: str):
        self.flow_id = flow_id
        self.path = format_path_declaration(path)
        self.methods = methods
        self.framework = framework

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "path": self.path,
            "methods": self.methods,
            "framework": self.framework,
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class KafkaDeclaration(Event):
    def __init__(
        self, flow_id: str, topic_name: str, group_id: Optional[str], pulling_type: str
    ):
        self.flow_id = flow_id
        self.topic_name = topic_name
        self.group_id = group_id
        self.pulling_type = pulling_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "topic_name": self.topic_name,
            "group_id": self.group_id,
            "pulling_type": self.pulling_type,
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class ArqFunction(Event):
    def __init__(self, flow_id: str, arq_function_name: str):
        self.flow_id = flow_id
        self.arq_function_name = arq_function_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "arq_function_name": self.arq_function_name,
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class FlowMetric(EventWithPid):
    def __init__(
        self,
        flow_id: str,
        count: int,
        sum_duration: int,
        sum_squared_duration: float,
        timeslice: int,
        timestamp: datetime,
        sketch: Sketch,
    ):
        self.flow_id = flow_id
        self.count = count
        self.sum_duration = sum_duration
        self.sum_squared_duration = sum_squared_duration
        self.timeslice = timeslice
        self.timestamp = timestamp
        self.sketch = sketch

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "flow_id": self.flow_id,
            "count": self.count,
            "sum_duration": self.sum_duration,
            "sum_squared_duration": self.sum_squared_duration,
            "timeslice": self.timeslice,
            "timestamp": self.timestamp.isoformat(),
            "sketch": self.sketch.to_dict(),
        }
        return result

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"


class EndpointMetric(FlowMetric):
    def __init__(
        self,
        flow_id: str,
        count: int,
        sum_duration: int,
        sum_squared_duration: float,
        timeslice: int,
        timestamp: datetime,
        sketch: Sketch,
        status_code: int,
        method: str,
    ):
        super().__init__(
            flow_id,
            count,
            sum_duration,
            sum_squared_duration,
            timeslice,
            timestamp,
            sketch,
        )
        self.status_code = status_code
        self.method = method

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update(
            {
                "status_code": self.status_code,
                "method": self.method,
            }
        )
        return result

    @classmethod
    def get_version(cls) -> str:
        return "1.0.1"


class KafkaMetric(FlowMetric):
    def __init__(
        self,
        flow_id: str,
        count: int,
        sum_duration: int,
        sum_squared_duration: float,
        timeslice: int,
        timestamp: datetime,
        sketch: Sketch,
        partition: int,
        error: Optional[str],
        sum_consumed_duration: int,
        sum_squared_consumed_duration: float,
        sketch_consume: Sketch,
    ):
        super().__init__(
            flow_id,
            count,
            sum_duration,
            sum_squared_duration,
            timeslice,
            timestamp,
            sketch,
        )
        self.partition = partition
        self.error = error
        self.sum_consumed_duration = sum_consumed_duration
        self.sum_squared_consumed_duration = sum_squared_consumed_duration
        self.sketch_consume = sketch_consume

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update(
            {
                "partition": self.partition,
                "error": self.error,
                "sum_consumed_duration": self.sum_consumed_duration,
                "sum_squared_consumed_duration": self.sum_squared_consumed_duration,
                "sketch_consume": self.sketch_consume.to_dict(),
            }
        )
        return result


class ArqFunctionMetric(FlowMetric):
    def __init__(
        self,
        flow_id: str,
        count: int,
        sum_duration: int,
        sum_squared_duration: float,
        timeslice: int,
        timestamp: datetime,
        sketch: Sketch,
        e2e_sum_duration: int,
        e2e_sum_squared_duration: float,
        e2e_sketch: Sketch,
        errors: Optional[Dict[str, int]],
    ):
        super().__init__(
            flow_id,
            count,
            sum_duration,
            sum_squared_duration,
            timeslice,
            timestamp,
            sketch,
        )
        self.errors = errors
        self.e2e_sum_duration = e2e_sum_duration
        self.e2e_sum_squared_duration = e2e_sum_squared_duration
        self.e2e_sketch = e2e_sketch

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update(
            {
                "errors": self.errors,
                "e2e_sum_duration": self.e2e_sum_duration,
                "e2e_sum_squared_duration": self.e2e_sum_squared_duration,
                "e2e_sketch": self.e2e_sketch.to_dict(),
            }
        )
        return result


class FileDeclaration(Event):
    def __init__(self, file_path_checksum: int, file_checksum: int):
        self.file_path_checksum = file_path_checksum
        self.file_checksum = file_checksum

    @staticmethod
    def from_json_data(data: JSON) -> "FileDeclaration":
        if not isinstance(data, dict):
            raise ValueError("Invalid data")

        file_path_checksum = data.get("file_path_checksum")
        file_checksum = data.get("file_checksum")

        if not isinstance(file_path_checksum, int) or not isinstance(
            file_checksum, int
        ):
            raise ValueError("Invalid data")

        return FileDeclaration(file_path_checksum, file_checksum)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path_checksum": self.file_path_checksum,
            "file_checksum": self.file_checksum,
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"

    def __hash__(self) -> int:
        return hash((self.file_path_checksum, self.file_checksum))

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, FileDeclaration):
            return False
        return (
            self.file_path_checksum == value.file_path_checksum
            and self.file_checksum == value.file_checksum
        )


class FlowInvestigation(Event):
    def __init__(
        self,
        version: str,
        flow_type: str,
        flow_uuid: str,
        s3_pointer: str,
        timestamp: datetime,
        exceptions: List[Any],  # Investigation ExceptionInfo as dict :/
    ):
        self.version = version
        self.flow_type = flow_type
        self.flow_uuid = flow_uuid
        self.s3_pointer = s3_pointer
        self.timestamp = timestamp
        self.exceptions = exceptions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "flow_type": self.flow_type,
            "flow_uuid": self.flow_uuid,
            "s3_pointer": self.s3_pointer,
            "timestamp": self.timestamp,
            "exceptions": self.exceptions,
        }

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"
