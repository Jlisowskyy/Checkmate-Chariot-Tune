from abc import ABC, abstractmethod

from Utils.Logger import Logger, LogLevel


class BuildableModule(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _is_built_correctly: bool
    _expected_exec_path: str
    _obj_name: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, exec_path: str, obj_name: str) -> None:
        self._is_built_correctly = False
        self._expected_exec_path = exec_path
        self._obj_name = obj_name

    # ------------------------------
    # Base methods
    # ------------------------------

    async def build_engine(self) -> None:
        Logger().log_info(f"Building module with name: {self._obj_name}...", LogLevel.LOW_FREQ)
        try:
            await self._build_internal()
            self._is_built_correctly = True
        except Exception as e:
            Logger().log_error(f"Failed to build module: {self._obj_name} with error: {e}", LogLevel.LOW_FREQ)
            raise e
        Logger().log_info(f"Module with name: {self._obj_name} built correctly!", LogLevel.LOW_FREQ)

    def is_built_correctly(self) -> bool:
        return self._is_built_correctly

    def get_exec_path(self) -> str:
        if not self._is_built_correctly:
            raise Exception(f"Module: {self._obj_name} is not built correctly!")
        return self._expected_exec_path

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def _build_internal(self) -> None:
        pass
