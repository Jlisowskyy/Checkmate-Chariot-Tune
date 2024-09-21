from collections.abc import Callable
from enum import IntEnum

from Utils.Helpers import validate_list_str, validate_string, validate_dict_str_str, validate_dict_str_int


class UiType(IntEnum):
    StringList = 0
    String = 1
    StringStringDict = 2
    StringIntPairDict = 3


UiTypeValidatorDict: dict[UiType, Callable[[any], None]] = {
    UiType.StringList: validate_list_str,
    UiType.String: validate_string,
    UiType.StringStringDict: validate_dict_str_str,
    UiType.StringIntPairDict: validate_dict_str_int,
}

missing_validators = [ui_type for ui_type in UiType if ui_type not in UiTypeValidatorDict]
if missing_validators:
    raise KeyError(f"UiTypeValidatorDict missing validators for: {missing_validators}")


class ConfigSpecElement:
    # ------------------------------
    # Class fields
    # ------------------------------

    _name: str
    _ui_type: UiType
    _description: str
    _default_value: str | list[str] | dict[str, str] | dict[str, int]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, name: str, description: str, ui_type: UiType) -> None:
        self._name = name
        self._description = description
        self._ui_type = ui_type

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_ui_type(self) -> UiType:
        return self._ui_type

    def __str__(self) -> str:
        return f"ConfigSpecElement({self._name}, {self._description}, {self._ui_type})"
