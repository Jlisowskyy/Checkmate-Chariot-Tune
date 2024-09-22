from abc import abstractmethod, ABC
from collections.abc import Callable

from Modules.ModuleHelpers import ConfigSpecElement, extract_submodule_type, validate_submodule_spec_args, \
    extract_submodule_name, UiType
from Modules.SubModuleMgr import SubModuleMgr


# Note: for submodule config name should be same as constructor parameter name
class ModuleBuilder(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _submodules = list[ConfigSpecElement]
    _submodule_type: str
    _submodule_name: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, submodules: list[ConfigSpecElement], submodule_type: str, submodule_name: str) -> None:
        self._submodules = submodules
        self._submodule_type = submodule_type
        self._submodule_name = submodule_name

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_next_submodule_needed(self, json_config: dict[str, list[str]], name_prefix: str = ""
                                  ) -> ConfigSpecElement | None:
        return self._iter_submodules(
            json_config,
            name_prefix,
            lambda name, builder, _: builder.get_next_submodule_needed(json_config, name),
            lambda _, conf: conf
        )



    def get_build_spec(self, json_config: dict[str, list[str]], name_prefix: str = "") -> list[ConfigSpecElement]:
        full_spec: list[ConfigSpecElement] = []

        full_spec.extend(self._get_build_spec_internal(name_prefix))
        self._iter_submodules(
            json_config,
            name_prefix,
            lambda name, builder, _: full_spec.extend(builder.get_build_spec(json_config, name)),
            ModuleBuilder._missing_config_spec
        )

        return full_spec

    def get_config_spec(self, json_config: dict[str, list[str]], name_prefix: str = "") -> list[ConfigSpecElement]:
        full_spec: list[ConfigSpecElement] = []

        full_spec.extend(self._get_config_spec_internal(name_prefix))
        self._iter_submodules(
            json_config,
            name_prefix,
            lambda name, builder, _: full_spec.extend(builder.get_config_spec(json_config, name)),
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
        path_prefix = f"{name_prefix}.{self._submodule_type}.{self._submodule_name}"

        for submodule in self._submodules:
            submodule_full_path = f"{path_prefix}.{submodule.get_name()}"

            if submodule_full_path in json_config:
                module_names = json_config[submodule.get_name()]

                validate_submodule_spec_args(module_names, submodule.get_ui_type())

                submodule_type = extract_submodule_type(submodule.get_name())
                for module_name in module_names:
                    builder = SubModuleMgr().get_submodule(submodule_type, module_name)

                    result = on_hit(path_prefix, builder, submodule)

                    if result is not None:
                        return result
            else:
                result = on_miss(submodule.get_name(), submodule)

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
        if config_spec.get_ui_type() == UiType.String:
            modules.update({extract_submodule_name(config_spec.get_name()): builder.build(json_config, name_prefix)})
        elif config_spec.get_ui_type() == UiType.StringList:
            if extract_submodule_name(config_spec.get_name()) not in modules:
                modules[extract_submodule_name(config_spec.get_name())] = []

            modules[extract_submodule_name(config_spec.get_name())].append(builder.build(json_config, name_prefix))

    def _build_submodules(self, json_config: dict[str, list[str]], name_prefix: str = "") -> dict[str, any]:
        rv: dict[str, any] = {}

        self._iter_submodules(
            json_config,
            name_prefix,
            lambda name, builder, submodule: ModuleBuilder._add_built_module(rv, json_config, name, builder, submodule),
            ModuleBuilder._missing_config_spec
        )

        return rv

ModuleBuilderFactory = Callable[[], ModuleBuilder]
