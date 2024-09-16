from abc import ABC, abstractmethod
from collections.abc import Callable

from Utils.Logger import Logger, LogLevel


class BaseEngineModule(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _is_built_correctly: bool
    _expected_exec_path: str
    _engine_name: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, build_path: str, engine_name: str) -> None:
        self._is_built_correctly = False
        self._expected_exec_path = build_path
        self._engine_name = engine_name

    # ------------------------------
    # Base methods
    # ------------------------------

    async def build_engine(self, build_path: str) -> None:
        Logger().log_info(f"Building engine with name: {self._engine_name}...", LogLevel.LOW_FREQ)
        try:
            await self._build_engine_internal(build_path)
            self._is_built_correctly = True
        except Exception as e:
            Logger().log_error(f"Failed to build engine: {self._engine_name} with error: {e}", LogLevel.LOW_FREQ)
            raise e
        Logger().log_info(f"Engine with name: {self._engine_name} built correctly!", LogLevel.LOW_FREQ)

    def is_engine_built(self) -> bool:
        return self._is_built_correctly

    def get_engine_exec_path(self) -> str:
        if not self._is_built_correctly:
            raise Exception("Engine is not built correctly!")
        return self._expected_exec_path

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def _build_engine_internal(self, build_path: str) -> None:
        pass

    @abstractmethod
    async def _get_start_arguments(self) -> list[str]:
        pass

    @abstractmethod
    async def _get_param_command(self, param_name: str, param_value: str) -> str:
        pass


EngineFactoryMethods: dict[str, Callable[[str, dict[str, str]], 'BaseEngineModule']] = {}


def append_engine_factory_method(engine: str, factory: Callable[[str, dict[str, str]], 'BaseEngineModule']) -> None:
    if engine in EngineFactoryMethods:
        raise Exception("Engine factory method already exists!")
    EngineFactoryMethods[engine] = factory
