from enum import Enum, IntEnum
from typing import List, Dict

from Models.GlobalModels import *

class UiType(Enum):
    StringList = List[str]
    String = str
    StringStringDict = Dict[str, str]
    StringIntPairDict = Dict[str, int]
    StringDictStringStringDict = Dict[str, Dict[str, str]]


default_value_type = str | List[str] | Dict[str, str] | Dict[str, int] | None


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

class ConfigSpecElement(BaseModel):
    # ------------------------------
    # Class fields
    # ------------------------------

    name: str
    ui_type: str
    description: str
    default_value: str | List[str] | Dict[str, str] | Dict[str, int] | None
    is_optional: bool


class TaskCreateRequest(BaseModel):
    name: str
    description: str
    module_name: str


class TaskCreateResult(BaseModel):
    result: str
    task_id: int


class TaskInitResponse(BaseModel):
    worker_init_spec: ConfigSpecElement | None
    manager_init_spec: ConfigSpecElement | None
    result: str


class TaskOpRequestWithConfig(BaseModel):
    task_id: int
    config: str

class TaskInitRequest(BaseModel):
    task_id: int
    worker_init: Dict[str, List[str]]
    manager_init: Dict[str, List[str]]

class TaskOperationRequest(BaseModel):
    task_id: int


class TestTaskMinimalQuery(BaseModel):
    task_id: int
    name: str
    description: str
    module_name: str
    task_state: TaskState


class TaskMinimalQueryAllResponse(BaseModel):
    queries: List[TestTaskMinimalQuery]

class TaskConfigSpecResponse(BaseModel):
    result: str
    worker_config_spec: List[ConfigSpecElement]
    manager_config_spec: List[ConfigSpecElement]

class TestTaskFullQuery(BaseModel):
    result: str
    minimal_query: TestTaskMinimalQuery
    worker_init_config: Dict[str, List[str]] | None
    manager_init_config: Dict[str, List[str]] | None
    worker_build_config: str
    manager_build_config: str
    worker_config: str
    manager_config: str

class ModuleQueryResponse(BaseModel):
    modules: List[str]

class SubModuleQueryResponse(BaseModel):
    submodules: Dict[str, List[str]]
