from tests.conftest import create_client


def test_healthcheck_returns_ok() -> None:
    with create_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
