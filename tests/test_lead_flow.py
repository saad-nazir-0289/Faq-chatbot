from tests.conftest import create_client


def test_lead_capture_flow_completes() -> None:
    with create_client() as client:
        session = client.post("/chat/start").json()["session_id"]
        steps = [
            "I need a pricing estimate",
            "Morgan Lee",
            "morgan@example.com",
            "555-222-1212",
            "residential",
            "I want solar plus battery",
            "No, just send my details",
        ]

        response = None
        for step in steps:
            response = client.post("/chat/message", json={"session_id": session, "message": step})

    assert response is not None
    body = response.json()
    assert response.status_code == 200
    assert body["lead_submitted"] is True
    assert body["appointment_requested"] is False
