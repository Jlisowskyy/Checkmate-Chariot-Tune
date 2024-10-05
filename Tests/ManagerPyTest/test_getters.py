from fastapi.testclient import TestClient
from httpx import Response

from Manager.manager_main import Manager


def validate_post_getter(client: TestClient, url: str) -> Response:
    response = client.post(url)
    assert response.status_code == 200
    return response


def validate_get_getter(client: TestClient, url: str) -> Response:
    response = client.get(url)
    assert response.status_code == 200
    return response


def test_getters() -> None:
    with TestClient(Manager) as client:
        response = validate_post_getter(client, "/orchestrator/task/query/minimal")
        assert response.json() == {'queries': []}

        validate_get_getter(client, "/orchestrator/modules/get/available")
