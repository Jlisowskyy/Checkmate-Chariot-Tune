import os.path
from abc import ABC, abstractmethod

from Modules.Module import Module
from Utils.Helpers import validate_dict_str, validate_string
from Utils.Logger import Logger, LogLevel


class BuildableModule(ABC, Module):
    # ------------------------------
    # Class fields
    # ------------------------------

    _is_build_configured: bool
    _is_built_correctly: bool
    _build_dir: str | None
    _expected_exec_path: str | None
    _obj_name: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, obj_name: str) -> None:
        self._is_built_correctly = False
        self._is_build_configured = False

        self._build_dir = None
        self._expected_exec_path = None

        self._obj_name = obj_name

    # ------------------------------
    # Base methods
    # ------------------------------

    async def build_module(self) -> None:
        Logger().log_info(f"Building module with name: {self._obj_name}...", LogLevel.MEDIUM_FREQ)

        try:
            if not self._is_build_configured:
                raise Exception(f"Module: {self._obj_name} is not configured for build!")

            await self._build_internal()

            if os.path.isfile(self._expected_exec_path) and os.access(self._expected_exec_path, os.X_OK):
                self._is_built_correctly = True
            else:
                raise Exception(
                    f"Failed to build module: {self._obj_name} with error: file not found or not executable")

            self._is_built_correctly = True
        except Exception as e:
            Logger().log_error(f"Failed to build module: {self._obj_name} with error: {e}", LogLevel.MEDIUM_FREQ)
            raise e
        Logger().log_info(f"Module with name: {self._obj_name} built correctly!", LogLevel.MEDIUM_FREQ)

    async def configure_build(self, json: any, _: str) -> None:
        Logger().log_info(f"Configuring build for module: {self._obj_name}...", LogLevel.MEDIUM_FREQ)

        validate_dict_str(json)

        try:
            if "build_dir" not in json:
                raise Exception("No build_dir found in config")

            if "exec_path" not in json:
                raise Exception("No exec_path found in config")

            validate_string(json["build_dir"])
            validate_string(json["exec_path"])

            await self._configure_build_internal(json)
        except Exception as e:
            Logger().log_error(f"Failed to configure build for module: {self._obj_name} with error: {e}",
                               LogLevel.MEDIUM_FREQ)
            raise e

        self._build_dir = json["build_dir"]
        self._expected_exec_path = json["exec_path"]

        self._is_build_configured = True

        Logger().log_info(f"Module: {self._obj_name} configured for build!", LogLevel.MEDIUM_FREQ)

    def is_built_correctly(self) -> bool:
        return self._is_built_correctly

    def is_build_configured(self) -> bool:
        return self._is_build_configured

    def get_exec_path(self) -> str:
        if not self._is_built_correctly or not self._is_build_configured:
            raise Exception(f"Module: {self._obj_name} is not built correctly!")
        return self._expected_exec_path

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def _build_internal(self) -> None:
        pass

    @abstractmethod
    async def _configure_build_internal(self, json: dict[str, any]) -> None:
        pass

