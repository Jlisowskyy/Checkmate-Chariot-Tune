from Modules.ModuleBuilder import ModuleBuilder
from Modules.Submodules import *
from Utils.GlobalObj import GlobalObj


class SubModuleMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    def destroy(self) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_all_submodules(self) -> list[[str, list[str]]]:
        rv: list[[str, list[str]]] = []

        for submodule_type_name in SubModulesRegistry.SubModulesBuilders.keys():
            rv.append(
                [submodule_type_name, list(SubModulesRegistry.SubModulesBuilders[submodule_type_name].keys())])

        return rv

    def get_all_submodules_by_type(self, submodule_type_name: str) -> list[str]:
        if submodule_type_name not in SubModulesRegistry.SubModulesBuilders:
            raise ValueError(f"Submodule type {submodule_type_name} not found in SubModulesBuilders")
        return list(SubModulesRegistry.SubModulesBuilders[submodule_type_name].keys())

    def get_submodule(self, submodule_type_name: str, submodule_name: str) -> ModuleBuilder:
        if submodule_type_name not in SubModulesRegistry.SubModulesBuilders:
            raise ValueError(f"Submodule type {submodule_type_name} not found in SubModulesBuilders")
        if submodule_name not in SubModulesRegistry.SubModulesBuilders[submodule_type_name]:
            raise ValueError(f"Submodule {submodule_name} not found in SubModulesBuilders[{submodule_type_name}]")
        return SubModulesRegistry.SubModulesBuilders[submodule_type_name][submodule_name]()

    def validate_submodule(self, submodule_type_name: str, submodule_name: str) -> None:
        if submodule_type_name not in SubModulesRegistry.SubModulesBuilders:
            raise ValueError(f"Submodule type {submodule_type_name} not found")
        if submodule_name not in SubModulesRegistry.SubModulesBuilders[submodule_type_name]:
            raise ValueError(f"Submodule {submodule_name} not found in SubModulesBuilders[{submodule_type_name}]")

    # ------------------------------
    # Private methods
    # ------------------------------
