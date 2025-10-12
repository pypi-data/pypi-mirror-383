from typing import Dict, List, Optional  # noqa: F401

from ._internal import worker_queue
from .schemas.events import ArqFunction
from .utils import calculate_uuid


class ArqDeclarationManager:
    def __init__(self) -> None:
        self._arq_function_to_id = {}  # type: Dict[str, str]

    def save_arq_declaration(
        self,
        arq_function_name: str,
    ) -> str:
        flow_id = self.get_arq_function_id(arq_function_name)
        if flow_id:
            return flow_id

        flow_id = str(calculate_uuid(arq_function_name))

        endpoint_declaration = ArqFunction(flow_id, arq_function_name)
        worker_queue.append(endpoint_declaration)

        self._arq_function_to_id[arq_function_name] = flow_id

        return flow_id

    def get_arq_function_id(self, arq_function_name: str) -> Optional[str]:
        return self._arq_function_to_id.get(arq_function_name)


class ArqDeclarationsAggregator:
    def __init__(self) -> None:
        self.declarations = []  # type: List[ArqFunction]

    def add_declaration(self, declaration: ArqFunction) -> None:
        self.declarations.append(declaration)

    def get_and_clear_declarations(self) -> List[ArqFunction]:
        declarations = [declaration for declaration in self.declarations]
        self.clear()
        return declarations

    def clear(self) -> None:
        self.declarations = []
