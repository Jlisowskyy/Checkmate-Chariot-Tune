from collections.abc import Callable

SubModulesFactoryMethods: dict[str, dict[str, Callable[[dict[str, str]], object]]] = {}


def append_submodule_factory_methods(module_name: str,
                                     factory_methods: dict[str, Callable[[dict[str, str]], object]]) -> None:
    if module_name not in SubModulesFactoryMethods:
        SubModulesFactoryMethods[module_name] = factory_methods
