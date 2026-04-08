from tests.conftest import create_client


def test_admin_seed_and_exports_work() -> None:
    with create_client() as client:
        seed = client.post("/admin/demo/seed")
        stats = client.get("/admin/stats")
        leads_csv = client.get("/admin/exports/leads.csv")
        appointments_csv = client.get("/admin/exports/appointments.csv")
        conversations = client.get("/admin/conversations")

    assert seed.status_code == 200
    assert seed.json()["inserted_leads"] == 2
    assert stats.status_code == 200
    assert stats.json()["lead_count"] >= 2
    assert leads_csv.status_code == 200
    assert "text/csv" in leads_csv.headers["content-type"]
    assert "Ava Brooks" in leads_csv.text
    assert appointments_csv.status_code == 200
    assert "Bright Bean Cafe" in appointments_csv.text
    assert conversations.status_code == 200
    assert len(conversations.json()) >= 1
