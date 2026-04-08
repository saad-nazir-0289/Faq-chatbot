from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    with TestClient(app) as client:
        session = client.post("/chat/start").json()["session_id"]
        faq_response = client.post(
            "/chat/message",
            json={"session_id": session, "message": "How long does installation take?"},
        )

    print("Smoke test status:", faq_response.status_code)
    print("Smoke test message:", faq_response.json()["message"])


if __name__ == "__main__":
    main()
