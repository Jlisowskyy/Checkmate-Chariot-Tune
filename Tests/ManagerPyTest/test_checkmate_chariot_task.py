from fastapi.testclient import TestClient

from Manager.manager_main import Manager
from Tests.ManagerPyTest.test_validators import validate_post_payload


def test_checkmate_chariot_task() -> None:
    with TestClient(Manager) as client:
        response = validate_post_payload(client, "/orchestrator/task/create",
                              {
                                  "name" : "test_task",
                                  "description" : "test_task",
                                  "module_name" : "BaseChessModule"
                              })

        assert response.json()["result"] == ""
