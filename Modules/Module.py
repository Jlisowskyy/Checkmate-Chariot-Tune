from abc import abstractmethod, ABC

class Module(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _module_name: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str) -> None:
        self._module_name = module_name


    # ------------------------------
    # Usual Methods
    # ------------------------------

    def get_module_name(self) -> str:
        return self._module_name

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    @abstractmethod
    async def build_module(self) -> None:
        pass

    @abstractmethod
    async def configure_module(self, json_parsed: any, prefix: str = "") -> None:
        pass

    @abstractmethod
    async def configure_build(self, json: any, prefix: str = "") -> None:
        pass
