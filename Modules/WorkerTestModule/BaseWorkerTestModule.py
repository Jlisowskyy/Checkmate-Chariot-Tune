from abc import abstractmethod, ABC
from typing import Callable


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


WorkerTestModuleFactoryMethods: dict[str, Callable[[dict[str, str]], BaseWorkerTestModule]] = {}


def append_test_module_factory_method(module: str, factory: Callable[[dict[str, str]], BaseWorkerTestModule]) -> None:
    if module not in WorkerTestModuleFactoryMethods:
        WorkerTestModuleFactoryMethods[module] = factory
