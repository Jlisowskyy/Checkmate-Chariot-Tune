from abc import ABC

from Modules.Module import Module


class NonConfigurableModule(ABC, Module):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str) -> None:
        super().__init__(module_name)

    # ------------------------------
    # Base methods
    # ------------------------------

    async def configure_module(self, json: str) -> None:
        return
