from collections.abc import Callable
from enum import Enum

from Utils.Helpers import validate_list_str, validate_string, validate_dict_str_str, validate_dict_str_int, \
    validate_string_dict_string_string_dict


# ------------------------------
# Ui Type
# ------------------------------

class UiType(Enum):
    StringList = list[str]
    String = str
    StringStringDict = dict[str, str]
    StringIntPairDict = dict[str, int]
    StringDictStringStringDict = dict[str, dict[str, str]]


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


# ------------------------------
# Config Spec Element
# ------------------------------

class ConfigSpecElement:
    default_value_type = str | list[str] | dict[str, str] | dict[str, int] | None

    # ------------------------------
    # Class fields
    # ------------------------------

    _name: str
    _ui_type: UiType
    _description: str
    _default_value: default_value_type
    _is_optional: bool

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, name: str, description: str, ui_type: UiType, default_value: default_value_type,
                 is_optional: bool) -> None:
        self._name = name
        self._description = description
        self._ui_type = ui_type
        self._default_value = default_value
        self._is_optional = is_optional

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_ui_type(self) -> UiType:
        return self._ui_type

    def get_default_value(self) -> default_value_type:
        return self._default_value

    def is_optional(self) -> bool:
        return self._is_optional

    def __str__(self) -> str:
        return f"ConfigSpecElement({self._name}, {self._description}, {self._ui_type})"


def build_config_spec_element(
        submodule_name: str,
        variable_name: str,
        description: str,
        ui_type: UiType,
        default_value: ConfigSpecElement.default_value_type,
        is_optional: bool
) -> ConfigSpecElement:
    if default_value is not None and not isinstance(default_value, ui_type.value):
        raise ValueError(f"Default value type must be {ui_type.value}, got {type(default_value)}")

    return ConfigSpecElement(get_typed_name(submodule_name, variable_name), description, ui_type, default_value, is_optional)


def build_submodule_spec_element(
        submodule_type: str,
        variable_name: str,
        description: str,
        ui_type: UiType,
        default_value: list[str]
) -> ConfigSpecElement:
    if ui_type != UiType.String or UiType.StringList:
        raise ValueError(f"Submodule spec element must have UiType.String or UiType.StringList, got {ui_type}")

    validate_list_str(default_value)
    return ConfigSpecElement(
        get_typed_name(submodule_type, variable_name),
        description,
        ui_type,
        default_value,
        False
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
