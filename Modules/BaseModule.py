from abc import abstractmethod, ABC


class BaseModule(ABC):
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
