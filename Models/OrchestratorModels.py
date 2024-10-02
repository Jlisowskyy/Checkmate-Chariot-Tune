from enum import Enum, IntEnum

from .GlobalModels import *


class UiType(Enum):
    StringList = list[str]
    String = str
    StringStringDict = dict[str, str]
    StringIntPairDict = dict[str, int]
    StringDictStringStringDict = dict[str, dict[str, str]]


default_value_type = str | list[str] | dict[str, str] | dict[str, int] | None


class TaskState(IntEnum):
    UNINITIATED = 0
    INITIATED = 1
    BUILT = 2
    READY = 3
    SCHEDULED = 4

class WorkerState(IntEnum):
    REGISTERED = 0
    CONNECTED = 1
    CONFIGURED = 2
    MARKED_FOR_DELETE = 3


class JobState(IntEnum):
    CREATED = 0
    PREPARED = 1
    INFLIGHT = 2
    COMPLETED = 3
    FAILED = 4
    HARDENED = 5

WORKABLE_STATES = [JobState.PREPARED, JobState.COMPLETED]
QUEUEABLE_STATES = [JobState.PREPARED, JobState.INFLIGHT, JobState.COMPLETED, JobState.FAILED]

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


class TestTaskMinimalQuery(BaseModel):
    task_id: int
    name: str
    description: str
    module_name: str
    task_state: TaskState


class TaskMinimalQueryAllResponse(BaseModel):
    queries: list[TestTaskMinimalQuery]

class TaskConfigSpecResponse(BaseModel):
    result: str
    worker_config_spec: list[ConfigSpecElement]
    manager_config_spec: list[ConfigSpecElement]

class TestTaskFullQuery(BaseModel):
    minimal_query: TestTaskMinimalQuery
    worker_init_config: dict[str, list[str]] | None
    manager_init_config: dict[str, list[str]] | None
    worker_build_config: dict[str, any] | None
    manager_build_config: dict[str, any] | None
    worker_config: dict[str, any] | None
    manager_config: dict[str, any] | None


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

