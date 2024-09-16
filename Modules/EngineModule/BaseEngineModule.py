from abc import ABC, abstractmethod
from collections.abc import Callable
from ..BuildableModule import BuildableModule


class BaseEngineModule(BuildableModule, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, exec_path: str, engine_name: str) -> None:
        super().__init__(exec_path, engine_name)

    # ------------------------------
    # Base methods
    # ------------------------------

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def get_config(self) -> dict[str, str]:
        pass

    @abstractmethod
    async def _get_param_command(self, param_name: str, param_value: str) -> str:
        pass


EngineFactoryMethods: dict[str, Callable[[str, dict[str, str]], 'BaseEngineModule']] = {}


def append_engine_factory_method(engine: str, factory: Callable[[str, dict[str, str]], 'BaseEngineModule']) -> None:
    if engine not in EngineFactoryMethods:
        EngineFactoryMethods[engine] = factory
