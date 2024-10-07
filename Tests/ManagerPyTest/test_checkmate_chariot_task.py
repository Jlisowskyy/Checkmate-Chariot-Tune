import json
from typing import Dict, List

from fastapi.testclient import TestClient

from Manager.manager_main import Manager
from Models.OrchestratorModels import TaskState
from Modules.ModuleHelpers import extract_submodule_type
from Tests.ManagerPyTest.validators import validate_post_payload, validate_get_getter


def add_default_modules(result: dict[str, list[str]], response: dict) -> bool:
    if response is None or response["default_value"] is None:
        return False

    var_name = response["name"]
    var_value = response["default_value"]

    result[var_name] = var_value

    return True


def add_non_default_modules(client: TestClient, result: dict[str, list[str]], response: dict) -> bool:
    if response is None or response["default_value"] is not None:
        return False

    var_name = response["name"]

    module_type = extract_submodule_type(var_name)

    submodules = validate_get_getter(client, "/orchestrator/submodules/get/active")

    assert module_type in submodules.json()["submodules"]
    assert len(submodules.json()["submodules"][module_type]) > 0

    var_value = submodules.json()["submodules"][module_type][0]

    result[var_name] = var_value


def validate_task_create(client: TestClient) -> int:
    # Correct task creation
    response = validate_post_payload(client, "/orchestrator/task/create",
                                     {
                                         "name": "test_task",
                                         "description": "test_task",
                                         "module_name": "BaseChessModule"
                                     })

    assert response.json()["result"] == ""
    assert response.json()["task_id"] != -1
    task_id = response.json()["task_id"]

    # Incorrect task creations
    response = validate_post_payload(client, "/orchestrator/task/create",
                                     {
                                         "name": "test_task",
                                         "description": "test_task",
                                         "module_name": "BaseChessModule"
                                     })

    assert response.json()["result"] != ""
    assert response.json()["task_id"] == -1

    response = validate_post_payload(client, "/orchestrator/task/create",
                                     {
                                         "name": "test_task_1",
                                         "description": "test_task_1",
                                         "module_name": "cvsiofjaspdfjasdfjasldkfaspdfojas"
                                     })

    assert response.json()["result"] != ""
    assert response.json()["task_id"] == -1

    return task_id


def validate_full_query(client: TestClient, task_id: int) -> None:
    response = validate_post_payload(client, "/orchestrator/task/query/full",
                                     {
                                         "task_id": task_id
                                     })

    assert response.json()["result"] == ""
    assert response.json()["minimal_query"]["task_id"] == task_id
    assert response.json()["minimal_query"]["name"] == "test_task"
    assert response.json()["minimal_query"]["description"] == "test_task"
    assert response.json()["minimal_query"]["module_name"] == "BaseChessModule"
    assert response.json()["minimal_query"]["task_state"] == TaskState.UNINITIATED.value

    assert response.json()["worker_init_config"] is None
    assert response.json()["manager_init_config"] is None
    assert response.json()["worker_build_config"] == ""
    assert response.json()["manager_build_config"] == ""
    assert response.json()["worker_config"] == ""
    assert response.json()["manager_config"] == ""

    response = validate_post_payload(client, "/orchestrator/task/query/full",
                                     {
                                         "task_id": -999
                                     })
    assert response.json()["result"] != ""


def validate_init(client: TestClient, task_id: int) -> None:
    retries = 10

    worker_init: Dict[str, List[str]] = {}
    manager_init: Dict[str, List[str]] = {}
    payload = {
        "task_id": task_id,
        "worker_init": worker_init,
        "manager_init": manager_init
    }

    response = validate_post_payload(client, "/orchestrator/task/init", payload)
    assert response.json()["result"] == ""

    while retries > 0:
        print(json.dumps(response.json(), indent=2))

        option_added = False

        for opt_name in ["worker_init", "manager_init"]:
            full_response_name = f"{opt_name}_spec"

            option_added = option_added | add_default_modules(payload[opt_name], response.json()[full_response_name])
            option_added = option_added | add_non_default_modules(client, payload[opt_name],
                                                                  response.json()[full_response_name])

        if not option_added:
            break

        print(json.dumps(payload, indent=2))
        print("-" * 80)
        response = validate_post_payload(client, "/orchestrator/task/init", payload)
        assert response.json()["result"] == ""

        retries -= 1

    assert retries > 0

    # Try to init a task that is already initialized
    response = validate_post_payload(client, "/orchestrator/task/init", payload)
    assert response.json()["result"] != ""

def validate_specs(client: TestClient, task_id: int) -> None:
    response = validate_post_payload(client, "/orchestrator/task/config/spec",
                                     {
                                         "task_id": task_id
                                     })

    assert response.json()["result"] == ""

    response = validate_post_payload(client, "/orchestrator/task/build/spec",
                                     {
                                         "task_id": task_id
                                     })

    assert response.json()["result"] == ""


def test_checkmate_chariot_task() -> None:
    with TestClient(Manager) as client:
        task_id = validate_task_create(client)
        validate_full_query(client, task_id)
        validate_init(client, task_id)
        validate_specs(client, task_id)