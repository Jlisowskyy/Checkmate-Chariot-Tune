from abc import ABC, abstractmethod
from collections.abc import Callable

from Modules.BuildableModule import BuildableModule
from ..SubModulesRegistry import append_submodule_builders
from ...ModuleBuilder import ModuleBuilder, ModuleBuilderFactory


class BaseEngineModule(BuildableModule, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBMODULE_TYPE = "Engine"

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str) -> None:
        super().__init__(module_name)

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
    async def get_param_command(self, param_name: str, param_value: str) -> str:
        pass


EngineModuleBuilders: dict[str, ModuleBuilderFactory] = {}
append_submodule_builders(BaseEngineModule.SUBMODULE_TYPE, EngineModuleBuilders)


def append_engine_builder(engine: str, builder: ModuleBuilderFactory) -> None:
    if engine not in EngineModuleBuilders:
        EngineModuleBuilders[engine] = builder
