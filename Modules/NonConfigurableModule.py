from abc import ABC

from Modules.Module import Module


class NonConfigurableModule(ABC, Module):
    async def configure_module(self, json: str) -> None:
        return
