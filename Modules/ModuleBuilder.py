from abc import abstractmethod, ABC
from collections.abc import Callable

from Models.OrchestratorModels import ConfigSpecElement, UiType
from Modules.ModuleHelpers import extract_submodule_type, validate_submodule_spec_args, \
    extract_submodule_variable_name


# Note: for submodule config name should be same as constructor parameter name
class ModuleBuilder(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _submodules: list[ConfigSpecElement]
    _submodule_name: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, submodules: list[ConfigSpecElement], submodule_name: str) -> None:
        self._submodules = submodules
        self._submodule_name = submodule_name

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_next_submodule_needed(self, json_config: dict[str, list[str]], name_prefix: str = ""
                                  ) -> ConfigSpecElement | None:
        return self._iter_submodules(
            json_config,
            name_prefix,
            lambda prefix, builder, _: builder.get_next_submodule_needed(json_config, prefix),
            lambda _, conf: conf
        )



    def get_build_spec(self, json_config: dict[str, list[str]], name_prefix: str = "") -> list[ConfigSpecElement]:
        full_spec: list[ConfigSpecElement] = []

        full_spec.extend(self._get_build_spec_internal(name_prefix))
        self._iter_submodules(
            json_config,
            name_prefix,
            lambda prefix, builder, _: full_spec.extend(builder.get_build_spec(json_config, prefix)),
            ModuleBuilder._missing_config_spec
        )

        return full_spec

    def get_config_spec(self, json_config: dict[str, list[str]], name_prefix: str = "") -> list[ConfigSpecElement]:
        full_spec: list[ConfigSpecElement] = []

        full_spec.extend(self._get_config_spec_internal(name_prefix))
        self._iter_submodules(
            json_config,
            name_prefix,
            lambda prefix, builder, _: full_spec.extend(builder.get_config_spec(json_config, prefix)),
            ModuleBuilder._missing_config_spec
        )

        return full_spec

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    def build(self, json_config: dict[str, list[str]], name_prefix: str = "") -> any:
        pass

    @abstractmethod
    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        pass

    @abstractmethod
    def _get_build_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------

    def _iter_submodules(self,
                         json_config: dict[str, list[str]],
                         name_prefix: str,
                         on_hit: Callable[[str, 'ModuleBuilder', ConfigSpecElement], any],
                         on_miss: Callable[[str, ConfigSpecElement], any]
                         ) -> any:
        from Modules.SubModuleMgr import SubModuleMgr

        for submodule in self._submodules:
            submodule_full_path = f"{name_prefix}.{submodule.name}"

            if submodule_full_path in json_config:
                module_names = json_config[submodule_full_path]

                validate_submodule_spec_args(module_names, submodule.ui_type)

                submodule_type = extract_submodule_type(submodule.name)
                for module_name in module_names:
                    builder = SubModuleMgr().get_submodule(submodule_type, module_name)

                    var_name = extract_submodule_variable_name(submodule.name)
                    path_prefix = f"{name_prefix}.{var_name}"
                    result = on_hit(path_prefix, builder, submodule)

                    if result is not None:
                        return result
            else:
                result = on_miss(submodule.name, submodule)

                if result is not None:
                    return result

        return None

    @staticmethod
    def _missing_config_spec(name: str, conf: ConfigSpecElement) -> None:
        raise ValueError(f"Missing json entry for submodule in path: {name} and spec: {conf}")

    @staticmethod
    def _add_built_module(
            modules: dict[str, any],
            json_config: dict[str, list[str]],
            name_prefix: str,
            builder: 'ModuleBuilder',
            config_spec: ConfigSpecElement
    ) -> None:
        if config_spec.ui_type == UiType.String:
            modules.update(
                {extract_submodule_variable_name(config_spec.name): builder.build(json_config, name_prefix)})
        elif config_spec.ui_type == UiType.StringList:
            if extract_submodule_variable_name(config_spec.name) not in modules:
                modules[extract_submodule_variable_name(config_spec.name)] = []

            modules[extract_submodule_variable_name(config_spec.name)].append(
                builder.build(json_config, name_prefix))

    def _build_submodules(self, json_config: dict[str, list[str]], name_prefix: str = "") -> dict[str, any]:
        rv: dict[str, any] = {}

        self._iter_submodules(
            json_config,
            name_prefix,
            lambda prefix, builder, submodule: ModuleBuilder._add_built_module(rv, json_config, prefix, builder,
                                                                               submodule),
            ModuleBuilder._missing_config_spec
        )

        return rv

ModuleBuilderFactory = Callable[[], ModuleBuilder]
