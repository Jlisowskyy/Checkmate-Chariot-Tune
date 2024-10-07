from abc import abstractmethod, ABC
from collections.abc import Callable

from Models.OrchestratorModels import ConfigSpecElement, UiType
from Modules.ModuleHelpers import extract_submodule_type, validate_submodule_spec_args, \
    extract_submodule_variable_name


# TODO: REWORK INIT TO SAME MANNER

# Note: for submodule config name should be same as constructor parameter name
class ModuleBuilder(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # Names should be simple manner: {submodule_type}.{variable_name}
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
            ModuleBuilder._prepare_init_spec
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
            submodule_type = extract_submodule_type(submodule.name)
            var_name = extract_submodule_variable_name(submodule.name)

            submodule_full_path = f"{submodule_type}.{name_prefix}.{var_name}" if name_prefix != "" else submodule.name

            if submodule_full_path in json_config:
                module_names = json_config[submodule_full_path]

                validate_submodule_spec_args(module_names, UiType[submodule.ui_type])

                for module_name in module_names:
                    builder = SubModuleMgr().get_submodule(submodule_type, module_name)

                    next_name_prefix = f"{name_prefix}.{var_name}" if name_prefix != "" else var_name
                    result = on_hit(next_name_prefix, builder, submodule)

                    if result is not None:
                        return result
            else:
                result = on_miss(name_prefix, submodule)

                if result is not None:
                    return result

        return None

    @staticmethod
    def _missing_config_spec(prefix: str, conf: ConfigSpecElement) -> None:
        raise ValueError(f"Missing json entry for submodule in path: {prefix} and spec: {conf}")

    @staticmethod
    def _prepare_init_spec(prefix: str, conf: ConfigSpecElement) -> ConfigSpecElement:
        submodule_type = extract_submodule_type(conf.name)
        var_name = extract_submodule_variable_name(conf.name)
        updated_name = f"{submodule_type}.{prefix}.{var_name}" if prefix != "" else f"{submodule_type}.{var_name}"

        copied_conf = conf.model_copy(deep=True, update={"name": updated_name})

        return copied_conf

    @staticmethod
    def _add_built_module(
            modules: dict[str, any],
            json_config: dict[str, list[str]],
            name_prefix: str,
            builder: 'ModuleBuilder',
            config_spec: ConfigSpecElement
    ) -> None:
        ui_type = UiType[config_spec.ui_type]
        if ui_type == UiType.String:
            modules.update(
                {extract_submodule_variable_name(config_spec.name): builder.build(json_config, name_prefix)})
        elif ui_type == UiType.StringList:
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
