from tests.conftest import create_client


def test_faq_question_returns_demo_answer() -> None:
    with create_client() as client:
        session = client.post("/chat/start").json()["session_id"]
        response = client.post(
            "/chat/message",
            json={"session_id": session, "message": "How much does a typical installation cost?"},
        )

    body = response.json()
    assert response.status_code == 200
    assert body["state"] == "detect_intent"
    assert "Northstar Solar" in body["message"] or "$12,000" in body["message"]
