from abc import abstractmethod, ABC

from Modules.Module import Module
from Modules.ModuleBuilder import ModuleBuilderFactory


class BaseWorkerTestModule(Module, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, submodule_name: str) -> None:
        super().__init__(submodule_name)

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def run_single_test(self, arg_str: str, seed: int) -> str:
        pass


WorkerTestModuleBuilders: dict[str, ModuleBuilderFactory] = {}


def append_test_module_builder(module: str, builder: ModuleBuilderFactory) -> None:
    if module not in WorkerTestModuleBuilders:
        WorkerTestModuleBuilders[module] = builder
