from abc import ABC

from Modules.Module import Module


class NonBuildableModule(ABC, Module):
    async def build_module(self) -> None:
        return
