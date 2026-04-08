from tests.conftest import create_client


def test_consultation_request_flow_completes() -> None:
    with create_client() as client:
        session = client.post("/chat/start").json()["session_id"]
        steps = [
            "Request a consultation",
            "Avery Stone",
            "avery@example.com",
            "555-444-7788",
            "Bright Bean Cafe",
            "Need a commercial solar estimate",
            "Yes, request a consultation",
            "Friday",
            "10 AM",
            "Please call before noon",
        ]

        response = None
        for step in steps:
            response = client.post("/chat/message", json={"session_id": session, "message": step})

    assert response is not None
    body = response.json()
    assert response.status_code == 200
    assert body["lead_submitted"] is True
    assert body["appointment_requested"] is True
