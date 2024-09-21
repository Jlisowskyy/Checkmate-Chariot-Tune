from abc import abstractmethod, ABC

from Modules.ModuleBuilder import ModuleBuilderFactory


class BaseWorkerTestModule(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def load_module_config_from_mgr(self, arg_str: str) -> None:
        pass

    @abstractmethod
    async def build_module(self) -> None:
        pass

    @abstractmethod
    async def run_single_test(self, arg_str: str, seed: int) -> str:
        pass


WorkerTestModuleBuilders: dict[str, ModuleBuilderFactory] = {}


def append_test_module_builder(module: str, builder: ModuleBuilderFactory) -> None:
    if module not in WorkerTestModuleBuilders:
        WorkerTestModuleBuilders[module] = builder
