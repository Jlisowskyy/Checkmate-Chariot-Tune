from enum import Enum

from .GlobalModels import *


class UiType(Enum):
    StringList = list[str]
    String = str
    StringStringDict = dict[str, str]
    StringIntPairDict = dict[str, int]
    StringDictStringStringDict = dict[str, dict[str, str]]


default_value_type = str | list[str] | dict[str, str] | dict[str, int] | None


# NEW MODELS

class ConfigSpecElement(BaseModel):
    # ------------------------------
    # Class fields
    # ------------------------------

    name: str
    ui_type: UiType
    description: str
    default_value: default_value_type
    is_optional: bool


class TaskCreateRequest(BaseModel):
    name: str
    description: str
    module_name: str


class TaskCreateResult(BaseModel):
    result: str
    task_id: int


class TaskInitResponse(BaseModel):
    worker_config_spec: ConfigSpecElement | None
    manager_config_spec: ConfigSpecElement | None
    result: str


class TaskOpRequestWithConfig(BaseModel):
    task_id: int
    config: str


class TaskOperationRequest(BaseModel):
    task_id: int


class TestTaskFullQuery(BaseModel):
    pass


# OLD MODELS

class TuneParameter(BaseModel):
    name: str
    min: int
    max: int


class TestDescription(BaseModel):
    name: str
    parameters: list[TuneParameter]
    commit: str
    passwordHash: str


class AuthInfo(BaseModel):
    passwordHash: str


class TestInfo(BaseModel):
    result: CommandResult
    tests: list[TestDescription]


class TestAccessInfo(BaseModel):
    auth: AuthInfo
    name: str


class TestResults(BaseModel):
    result: CommandResult
    parameters: list[int]


class File(BaseModel):
    name: str
    content: str


class Backup(BaseModel):
    result: CommandResult
    backup: list[File]
