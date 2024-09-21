from abc import abstractmethod, ABC
from collections.abc import Callable

from Modules.ModuleHelpers import ConfigSpecElement, UiType, validate_submodule_spec_string, \
    validate_submodule_spec_string_list, extract_submodule_type, validate_submodule_spec_args
from Modules.SubModuleMgr import SubModuleMgr


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
        for submodule in self._submodules:
            submodule_full_path = f"{name_prefix}.{self._submodule_type}.{self._submodule_name}.{submodule.get_name()}"

            if submodule_full_path in json_config:
                module_names = json_config[submodule_full_path]

                validate_submodule_spec_args(module_names, submodule.get_ui_type())

                submodule_type = extract_submodule_type(submodule.get_name())
                path_prefix = f"{name_prefix}.{self._submodule_type}.{self._submodule_name}"
                for module_name in module_names:
                    builder = SubModuleMgr().get_submodule(submodule_type, module_name)

                    next_submodule = builder.get_next_submodule_needed(json_config, path_prefix)

                    if next_submodule is not None:
                        return next_submodule
            else:
                return submodule

        return None

    def get_build_spec(self, json_config: dict[str, list[str]], name_prefix: str = "") -> list[ConfigSpecElement]:
        full_spec: list[ConfigSpecElement] = []

        path_prefix = f"{name_prefix}.{self._submodule_type}.{self._submodule_name}"
        build_spec = self._get_build_spec_internal(path_prefix)

        for submodule in self._submodules:
            submodule_full_path = f"{path_prefix}.{submodule.get_name()}"

            if submodule_full_path in json_config:
                module_names = json_config[submodule.get_name()]

                validate_submodule_spec_args(module_names, submodule.get_ui_type())

                submodule_type = extract_submodule_type(submodule.get_name())
                for module_name in module_names:
                    builder = SubModuleMgr().get_submodule(submodule_type, module_name)

                    next_submodule = builder.get_next_submodule_needed(json_config, path_prefix)

            else:
                return submodule

        return None

    def get_config_spec(self) -> list[ConfigSpecElement]:
        config_spec = self._get_config_spec_internal()

        for submodule in self._submodules:
            [mod_type, mod_name] = get_type_mod_name(submodule.get_name())
            builder = SubModuleMgr().get_submodule(mod_type, mod_name)

            config_spec += builder._get_config_spec_internal()

        return config_spec

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    def build(self, json_config: dict[str, str]) -> any:
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
                         on_hit: Callable[[str], None],
                         on_miss: Callable[[str], None]
                         ) -> None:
        path_prefix = f"{name_prefix}.{self._submodule_type}.{self._submodule_name}"

        for submodule in self._submodules:
            submodule_full_path = f"{path_prefix}.{submodule.get_name()}"

            if submodule_full_path in json_config:
                module_names = json_config[submodule.get_name()]

                validate_submodule_spec_args(module_names, submodule.get_ui_type())

                submodule_type = extract_submodule_type(submodule.get_name())
                for module_name in module_names:
                    builder = SubModuleMgr().get_submodule(submodule_type, module_name)

                    next_submodule = builder.get_next_submodule_needed(json_config, path_prefix)

            else:
                return submodule

ModuleBuilderFactory = Callable[[], ModuleBuilder]
