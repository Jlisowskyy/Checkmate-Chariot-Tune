from abc import abstractmethod, ABC
from typing import Callable


class BaseTestModule(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Worker methods
    # ------------------------------

    @abstractmethod
    async def load_module_config_from_mgr(self, arg_str: str) -> None:
        pass

    @abstractmethod
    async def build_module(self, build_path: str) -> None:
        pass

    @abstractmethod
    async def run_single_test(self, arg_str: str) -> None:
        pass

    # ------------------------------
    # Manager methods
    # ------------------------------

    @abstractmethod
    async def prepare_config_args(self) -> str:
        pass

    @abstractmethod
    async def prepare_test_args(self) -> str:
        pass

    @abstractmethod
    async def sync_test_results(self, response: str) -> None:
        pass

TestModuleFactoryMethods: dict[str, Callable[[dict[str, str]], BaseTestModule]] = {}

def append_test_module_factory_method(module: str, factory: Callable[[dict[str, str]], BaseTestModule]) -> None:
    if module not in TestModuleFactoryMethods:
        TestModuleFactoryMethods[module] = factory