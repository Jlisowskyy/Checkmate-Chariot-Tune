from fastapi.testclient import TestClient

from Manager.manager_main import Manager
from Tests.ManagerPyTest.validators import validate_post_payload


def test_checkmate_chariot_task() -> None:
    with TestClient(Manager) as client:
        response = validate_post_payload(client, "/orchestrator/task/create",
                              {
                                  "name" : "test_task",
                                  "description" : "test_task",
                                  "module_name" : "BaseChessModule"
                              })

        assert response.json()["result"] == ""
        assert response.json()["task_id"] != -1

        task_id = response.json()["task_id"]

        response = validate_post_payload(client, "/orchestrator/task/query/full",
                                         {
                                             "task_id": task_id
                                         })

        assert response.json()["result"] == ""
        assert response.json()["minimal_query"]["task_id"] == task_id
        assert response.json()["minimal_query"]["name"] == "test_task"
        assert response.json()["minimal_query"]["description"] == "test_task"

        response = validate_post_payload(client, "/orchestrator/task/init",
                                         {
                                             "task_id": task_id,
                                             "config": """{
                                                "worker_init" : {},
                                                "manager_init" : {}
                                             }"""
                                         })

        assert response.json()["result"] == ""
