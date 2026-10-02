"""Fixture and Notion persistence for the demo workflow."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from contracts.models import Event, FollowUpTask, OperationItem

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "contracts" / "fixtures" / "seed.json"


def load_local_env() -> None:
    """Load simple KEY=VALUE entries without ever printing their values."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def _page_value(page: dict[str, Any], name: str) -> Any:
    return page.get("properties", {}).get(name, {})


def _plain(page: dict[str, Any], name: str) -> str:
    prop = _page_value(page, name)
    for kind in ("title", "rich_text"):
        values = prop.get(kind, [])
        if values:
            return "".join(piece.get("plain_text", "") for piece in values)
    return ""


def _select(page: dict[str, Any], name: str, default: str = "") -> str:
    selected = _page_value(page, name).get("select") or {}
    return selected.get("name", default)


def _relations(page: dict[str, Any], name: str) -> list[str]:
    return [item["id"] for item in _page_value(page, name).get("relation", [])]


def _rich(text: str) -> dict[str, Any]:
    return {"rich_text": [{"text": {"content": text}}]}


class FixtureStore:
    mode = "fixtures"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.event = Event.model_validate(data["event"])
        self.items = [OperationItem.model_validate(row) for row in data["items"]]
        self.tasks = [FollowUpTask.model_validate(row) for row in data.get("tasks", [])]
        self.logs: list[dict[str, Any]] = data.get("impact_log", [])

    def load(self) -> tuple[Event, list[OperationItem], list[FollowUpTask]]:
        return self.event, self.items, self.tasks

    def apply(self, result: Any) -> None:
        if result.change_type == "venue":
            self.event.venue = result.to_value
            self.event.status = "Venue changed"
        elif result.change_type == "schedule":
            self.event.date = result.to_value
        affected_ids = {item.id for item in result.affected}
        for item in self.items:
            if result.change_type == "venue" and item.id in affected_ids and item.location.casefold() == result.from_value.casefold() or result.change_type == "deployment" and item.id == result.target_item_id:
                item.location = result.to_value
        known_task_ids = {task.id for task in self.tasks}
        self.tasks.extend(task for task in result.follow_up_tasks if task.id not in known_task_ids)
        self.logs.append(
            {"event_id": result.event_id, "type": result.change_type,
             "from": result.from_value, "to": result.to_value,
             "affected": sorted(affected_ids),
             "created_at": datetime.now(UTC).isoformat()}
        )

    def closeout(self, event_id: str, summary: str, lessons: str) -> None:
        self.event.status = "Done"
        self.logs.append({
            "event_id": event_id, "type": "closeout", "summary": summary,
            "lessons": lessons, "created_at": datetime.now(UTC).isoformat(),
        })


class NotionStore:
    mode = "notion"

    def __init__(self) -> None:
        load_local_env()
        token = os.getenv("NOTION_TOKEN", "")
        required = [
            "NOTION_EVENTS_DB", "NOTION_OPERATIONS_DB",
            "NOTION_EVENT_TASKS_DB", "NOTION_IMPACT_LOG_DB",
        ]
        missing = [key for key in required if not os.getenv(key)]
        if not token or missing:
            names = ("NOTION_TOKEN", *missing) if not token else tuple(missing)
            raise RuntimeError("Notion mode requires environment variables: " + ", ".join(names))
        self.http = httpx.Client(
            base_url="https://api.notion.com/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2026-03-11",
                "Content-Type": "application/json",
            },
            timeout=20,
        )
        self.db = {key: os.environ[key] for key in required}
        self.data_sources: dict[str, str] = {}

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.http.request(method, path, json=payload)
        if response.is_error:
            try:
                error = response.json()
                reason = f"{error.get('code', 'notion_error')}: {error.get('message', 'request failed')}"
            except ValueError:
                reason = "request failed"
            raise RuntimeError(f"Notion API {response.status_code}: {reason}")
        return response.json()

    def _data_source_id(self, database_id: str) -> str:
        if database_id not in self.data_sources:
            database = self._request("GET", f"/databases/{database_id}")
            sources = database.get("data_sources", [])
            if not sources:
                raise RuntimeError("Notion database has no accessible data source")
            self.data_sources[database_id] = sources[0]["id"]
        return self.data_sources[database_id]

    def _query(self, database_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor = None
        source_id = self._data_source_id(database_id)
        while True:
            args: dict[str, Any] = {"page_size": 100}
            if cursor:
                args["start_cursor"] = cursor
            response = self._request("POST", f"/data_sources/{source_id}/query", args)
            results.extend(response["results"])
            if not response.get("has_more"):
                return results
            cursor = response["next_cursor"]

    def load(self) -> tuple[Event, list[OperationItem], list[FollowUpTask]]:
        events = self._query(self.db["NOTION_EVENTS_DB"])
        event_page = next((p for p in events if _plain(p, "ID") == "EVT-001"), None)
        if event_page is None:
            raise RuntimeError("Notion Events database does not contain EVT-001")
        event = Event(
            id="EVT-001", name=_plain(event_page, "Name"),
            venue=_plain(event_page, "Venue"),
            date=(_page_value(event_page, "Date").get("date") or {}).get("start"),
            status=_select(event_page, "Status", "Planned"),
        )
        self.event_page_id = event_page["id"]
        pages = self._query(self.db["NOTION_OPERATIONS_DB"])
        id_by_page = {page["id"]: _plain(page, "ID") for page in pages}
        self.operation_pages = {_plain(page, "ID"): page for page in pages}
        items: list[OperationItem] = []
        for page in pages:
            if self.event_page_id not in _relations(page, "Event"):
                continue
            items.append(OperationItem(
                id=_plain(page, "ID"), name=_plain(page, "Name"), event_id=event.id,
                type=_select(page, "Type", "Session"),
                owner_role=_select(page, "Owner Role", "Operations"),
                status=_select(page, "Status", "Planned"),
                location=_plain(page, "Location"),
                depends_on=[id_by_page[pid] for pid in _relations(page, "Depends On") if pid in id_by_page],
                dependency_reason=_plain(page, "Dependency Reason"),
            ))
        task_pages = self._query(self.db["NOTION_EVENT_TASKS_DB"])
        tasks = [FollowUpTask(
            id=_plain(page, "ID"), name=_plain(page, "Name"), event_id=event.id,
            related_item_id="", owner_role=_select(page, "Owner Role", "Operations"),
            status=_select(page, "Status", "Todo"),
        ) for page in task_pages]
        return event, items, tasks

    def apply(self, result: Any) -> None:
        event_page_id = self.event_page_id
        event_properties: dict[str, Any] = {}
        if result.change_type == "venue":
            event_properties = {
                "Venue": _rich(result.to_value),
                "Status": {"select": {"name": "Venue changed"}},
            }
        elif result.change_type == "schedule":
            event_properties = {"Date": {"date": {"start": result.to_value}}}
        if event_properties:
            self._request("PATCH", f"/pages/{event_page_id}", {"properties": event_properties})
        for impacted in result.affected:
            page = self.operation_pages[impacted.id]
            should_update_location = (
                result.change_type == "venue"
                and _plain(page, "Location").casefold() == result.from_value.casefold()
            ) or (result.change_type == "deployment" and impacted.id == result.target_item_id)
            if should_update_location:
                self._request("PATCH", f"/pages/{page['id']}", {"properties": {"Location": _rich(result.to_value)}})

        existing_task_pages = {
            _plain(page, "ID"): page
            for page in self._query(self.db["NOTION_EVENT_TASKS_DB"])
        }
        task_page_ids: list[str] = []
        for task in result.follow_up_tasks:
            if task.id in existing_task_pages:
                task_page_ids.append(existing_task_pages[task.id]["id"])
                continue
            created = self._request("POST", "/pages", {
                "parent": {"data_source_id": self._data_source_id(self.db["NOTION_EVENT_TASKS_DB"])},
                "properties": {
                    "Name": {"title": [{"text": {"content": task.name}}]},
                    "ID": _rich(task.id),
                    "Owner Role": {"select": {"name": task.owner_role}},
                    "Status": {"select": {"name": "Todo"}},
                    "Event": {"relation": [{"id": event_page_id}]},
                    "Related Item": {"relation": [{"id": self.operation_pages[task.related_item_id]["id"]}]},
                },
            })
            task_page_ids.append(created["id"])

        self._request("POST", "/pages", {
            "parent": {"data_source_id": self._data_source_id(self.db["NOTION_IMPACT_LOG_DB"])},
            "properties": {
                "Name": {"title": [{"text": {"content": f"{result.change_type.title()} change: {result.from_value} → {result.to_value}"}}]},
                "ID": _rich(f"IMP-{result.event_id}-{result.change_type.upper()}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"),
                "Change": _rich(f"{result.change_type.title()}: {result.from_value} → {result.to_value}"),
                "Reason": _rich(f"{len(result.affected)} operations are directly or indirectly affected by this change."),
                "Created At": {"date": {"start": datetime.now(UTC).isoformat()}},
                "Event": {"relation": [{"id": event_page_id}]},
                "Affected": {"relation": [{"id": self.operation_pages[item.id]["id"]} for item in result.affected]},
                "Follow-ups": {"relation": [{"id": page_id} for page_id in task_page_ids]},
            },
        })

    def closeout(self, event_id: str, summary: str, lessons: str) -> None:
        self._request("PATCH", f"/pages/{self.event_page_id}", {
            "properties": {"Status": {"select": {"name": "Done"}}},
        })
        now = datetime.now(UTC)
        self._request("POST", "/pages", {
            "parent": {"data_source_id": self._data_source_id(self.db["NOTION_IMPACT_LOG_DB"])},
            "properties": {
                "Name": {"title": [{"text": {"content": "Event closeout"}}]},
                "ID": _rich(f"CLOSE-{event_id}-{now.strftime('%Y%m%d%H%M%S')}"),
                "Change": _rich(f"Event completed: {summary}"),
                "Reason": _rich(f"Lessons learned: {lessons}"),
                "Created At": {"date": {"start": now.isoformat()}},
                "Event": {"relation": [{"id": self.event_page_id}]},
                "Affected": {"relation": []},
                "Follow-ups": {"relation": []},
            },
        })


def create_store() -> FixtureStore | NotionStore:
    load_local_env()
    if os.getenv("USE_FIXTURES", "true").lower() == "true":
        return FixtureStore()
    return NotionStore()
