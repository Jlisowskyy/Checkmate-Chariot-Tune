from collections.abc import Callable

from Models.OrchestratorModels import ConfigSpecElement, UiType, default_value_type
from Utils.Helpers import validate_list_str, validate_string, validate_dict_str_str, validate_dict_str_int, \
    validate_string_dict_string_string_dict

# ------------------------------
# Ui Type
# ------------------------------


UiTypeValidatorDict: dict[UiType, Callable[[any], None]] = {
    UiType.StringList: validate_list_str,
    UiType.String: validate_string,
    UiType.StringStringDict: validate_dict_str_str,
    UiType.StringIntPairDict: validate_dict_str_int,
    UiType.StringDictStringStringDict: validate_string_dict_string_string_dict
}

missing_validators = [ui_type for ui_type in UiType if ui_type not in UiTypeValidatorDict]
if missing_validators:
    raise KeyError(f"UiTypeValidatorDict missing validators for: {missing_validators}")


def validate_obj_by_ui_type(ui_type: UiType, obj: any) -> None:
    if ui_type not in UiTypeValidatorDict:
        raise ValueError(f"Invalid UiType {ui_type}")
    UiTypeValidatorDict[ui_type](obj)

# ------------------------------
# Config Spec Element
# ------------------------------


def build_config_spec_element(
        submodule_name: str,
        variable_name: str,
        description: str,
        ui_type: UiType,
        default_value: default_value_type,
        is_optional: bool
) -> ConfigSpecElement:
    if default_value is not None:
        validate_obj_by_ui_type(ui_type, default_value)
        raise ValueError(f"Default value type must be {ui_type.value}, got {type(default_value)}")

    return ConfigSpecElement(name=get_typed_name(submodule_name, variable_name),
                             description=description,
                             ui_type=ui_type.name,
                             default_value=default_value,
                             is_optional=is_optional)

def build_submodule_spec_element(
        submodule_type: str,
        variable_name: str,
        description: str,
        ui_type: UiType,
        default_value: list[str]
) -> ConfigSpecElement:
    if ui_type != UiType.String and ui_type!= UiType.StringList:
        raise ValueError(f"Submodule spec element must have UiType.String or UiType.StringList, got {ui_type}")

    validate_list_str(default_value)
    return ConfigSpecElement(
        name=get_typed_name(submodule_type, variable_name),
        description=description,
        ui_type=ui_type.name,
        default_value=default_value,
        is_optional=False
    )


def get_typed_name(submodule_type: str, name: str) -> str:
    return f"{submodule_type}.{name}"

def extract_submodule_type(submodule_spec_name: str) -> str:
    return submodule_spec_name.split(".")[0]

def extract_submodule_variable_name(submodule_spec_name: str) -> str:
    return submodule_spec_name.split(".")[1]

def validate_submodule_spec_string(obj: list[str]) -> None:
    if len(obj) != 1:
        raise ValueError(f"Submodule spec string must have 1 elements, got {len(obj)}")


def validate_submodule_spec_string_list(obj: list[str]) -> None:
    if len(obj) < 1:
        raise ValueError(f"Submodule spec string list must have at least 1 element, got {len(obj)}")


def validate_submodule_spec_args(obj: list[str], ui_type: UiType) -> None:
    if ui_type == UiType.String:
        validate_submodule_spec_string(obj)
    elif ui_type == UiType.StringList:
        validate_submodule_spec_string_list(obj)
    else:
        raise ValueError(f"Invalid UiType {ui_type} for submodule spec args")

def get_config_prefixed_name(prefix: str, module_name: str, var_name: str) -> str:
    return f"{prefix}.{module_name}.{var_name}"
