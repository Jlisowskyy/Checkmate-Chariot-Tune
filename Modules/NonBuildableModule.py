from abc import ABC

from Modules.Module import Module


class NonBuildableModule(Module, ABC):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str) -> None:
        super().__init__(module_name)

    # ------------------------------
    # Basic Methods
    # ------------------------------

    async def build_module(self) -> None:
        return

    async def configure_build(self, json: any, prefix: str) -> None:
        return
