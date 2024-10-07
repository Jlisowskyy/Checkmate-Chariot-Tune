from fastapi.testclient import TestClient

from Manager.manager_main import Manager
from Tests.ManagerPyTest.validators import validate_post_getter, validate_get_getter


def test_getters() -> None:
    with TestClient(Manager) as client:
        response = validate_post_getter(client, "/orchestrator/task/query/minimal")
        assert response.json() == {'queries': []}

        validate_get_getter(client, "/orchestrator/modules/get/available")

        validate_get_getter(client, "/orchestrator/submodules/get/active")
