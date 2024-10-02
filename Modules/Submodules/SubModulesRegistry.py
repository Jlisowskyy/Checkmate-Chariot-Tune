from Modules.ModuleBuilder import ModuleBuilderFactory

SubModulesBuilders: dict[str, dict[str, ModuleBuilderFactory]] = {}


def append_submodule_builders(module_name: str,
                              builders: dict[str, ModuleBuilderFactory]) -> None:
    if module_name not in SubModulesBuilders:
        SubModulesBuilders[module_name] = builders
