import json
from pathlib import Path

from contracts.models import ChangeRequest, Event, OperationItem
from impact.evaluator import evaluate_change, evaluate_venue_change


def test_venue_change_returns_expected_downstream_records() -> None:
    seed = Path(__file__).parents[2] / "contracts" / "fixtures" / "seed.json"
    data = json.loads(seed.read_text(encoding="utf-8"))
    event = Event.model_validate(data["event"])
    items = [OperationItem.model_validate(row) for row in data["items"]]

    result = evaluate_venue_change(event, items, "Open Air Theatre")

    assert [item.id for item in result.affected] == [
        "OP-001", "OP-002", "OP-003", "OP-005", "OP-006", "OP-008", "OP-009", "OP-010", "OP-011"
    ]
    assert len(result.follow_up_tasks) == 9
    assert all(item.reason and item.dependency_path for item in result.affected)


def test_schedule_change_cascades_from_sessions() -> None:
    seed = Path(__file__).parents[2] / "contracts" / "fixtures" / "seed.json"
    data = json.loads(seed.read_text(encoding="utf-8"))
    event = Event.model_validate(data["event"])
    items = [OperationItem.model_validate(row) for row in data["items"]]

    result = evaluate_change(event, items, ChangeRequest(change_type="schedule", new_date="2026-10-11"))

    assert result.change_type == "schedule"
    assert result.from_value == "2026-10-10"
    assert {"OP-001", "OP-002", "OP-003", "OP-005", "OP-008", "OP-011"}.issubset(
        {item.id for item in result.affected}
    )
    assert all(item.reason and item.dependency_path for item in result.affected)


def test_deployment_change_starts_from_selected_resource() -> None:
    seed = Path(__file__).parents[2] / "contracts" / "fixtures" / "seed.json"
    data = json.loads(seed.read_text(encoding="utf-8"))
    event = Event.model_validate(data["event"])
    items = [OperationItem.model_validate(row) for row in data["items"]]

    result = evaluate_change(event, items, ChangeRequest(
        change_type="deployment", target_item_id="OP-008", new_location="Registration Atrium"
    ))

    assert [item.id for item in result.affected] == ["OP-008"]
    assert result.from_value == "Main Auditorium Lobby"
    assert result.to_value == "Registration Atrium"
    assert result.follow_up_tasks[0].owner_role == "Volunteers"
