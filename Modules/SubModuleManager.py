from collections.abc import Callable

from .Submodules import *


class SubModuleManager:
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_all_submodules(self) -> list[[str, list[str]]]:
        rv: list[[str, list[str]]] = []

        for submodule_type_name in SubModulesRegistry.SubModulesFactoryMethods.keys():
            rv.append(
                [submodule_type_name, list(SubModulesRegistry.SubModulesFactoryMethods[submodule_type_name].keys())])

        return rv

    def get_submodule(self, submodule_type_name: str, submodule_name: str) -> Callable[[dict[str, str]], object]:
        if submodule_type_name not in SubModulesRegistry.SubModulesFactoryMethods:
            raise ValueError(f"Submodule type {submodule_type_name} not found in SubModulesFactoryMethods")
        if submodule_name not in SubModulesRegistry.SubModulesFactoryMethods[submodule_type_name]:
            raise ValueError(f"Submodule {submodule_name} not found in SubModulesFactoryMethods[{submodule_type_name}]")
        return SubModulesRegistry.SubModulesFactoryMethods[submodule_type_name][submodule_name]

    # ------------------------------
    # Private methods
    # ------------------------------
