import os
from importlib import import_module

from fastapi.testclient import TestClient

# Unit tests must never write to a connected DEMO workspace.
os.environ["USE_FIXTURES"] = "true"
app = import_module("apps.api.app.main").app


def test_health() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "data_source": "fixtures"}


def test_preview_and_apply_venue_change() -> None:
    client = TestClient(app)
    preview = client.post("/api/events/EVT-001/preview", json={"new_venue": "Open Air Theatre"})
    assert preview.status_code == 200
    assert len(preview.json()["affected"]) == 9

    applied = client.post("/api/events/EVT-001/apply", json={"new_venue": "Open Air Theatre"})
    assert applied.status_code == 200
    assert client.get("/api/events/EVT-001/board").json()["event"]["venue"] == "Open Air Theatre"
    assert client.get("/api/events/EVT-001/board").json()["counts"]["tasks"] == 9
    assert client.post("/api/demo/reset").status_code == 200


def test_preview_and_apply_schedule_change() -> None:
    client = TestClient(app)
    assert client.post("/api/demo/reset").status_code == 200
    preview = client.post("/api/events/EVT-001/preview", json={
        "change_type": "schedule", "new_date": "2026-10-11",
    })
    assert preview.status_code == 200
    assert preview.json()["change_type"] == "schedule"
    assert len(preview.json()["affected"]) == 11
    applied = client.post("/api/events/EVT-001/apply", json={
        "change_type": "schedule", "new_date": "2026-10-11",
    })
    assert applied.status_code == 200
    assert client.get("/api/events/EVT-001/board").json()["event"]["date"] == "2026-10-11"
    assert client.post("/api/demo/reset").status_code == 200


def test_preview_and_apply_deployment_change() -> None:
    client = TestClient(app)
    assert client.post("/api/demo/reset").status_code == 200
    payload = {
        "change_type": "deployment", "target_item_id": "OP-008",
        "new_location": "Registration Atrium",
    }
    preview = client.post("/api/events/EVT-001/preview", json=payload)
    assert preview.status_code == 200
    assert [item["id"] for item in preview.json()["affected"]] == ["OP-008"]
    applied = client.post("/api/events/EVT-001/apply", json=payload)
    assert applied.status_code == 200
    volunteer = next(item for item in client.get("/api/events/EVT-001/board?role=Volunteers").json()["items"] if item["id"] == "OP-008")
    assert volunteer["location"] == "Registration Atrium"
    assert client.post("/api/demo/reset").status_code == 200


def test_event_closeout_records_status_and_lessons() -> None:
    client = TestClient(app)
    assert client.post("/api/demo/reset").status_code == 200
    response = client.post("/api/events/EVT-001/closeout", json={
        "summary": "Demo event completed with all activities on schedule.",
        "lessons": "Keep a second equipment check before the opening session.",
    })
    assert response.status_code == 200
    assert client.get("/api/events/EVT-001/board").json()["event"]["status"] == "Done"
    assert client.post("/api/demo/reset").status_code == 200
