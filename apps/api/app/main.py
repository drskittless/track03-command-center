"""Small API for the event operations demo."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from contracts.models import (
    ChangeRequest,
    Event,
    EventCloseoutRequest,
    ImpactResult,
    OperationItem,
    Role,
)
from impact.evaluator import evaluate_change

from .store import create_store

app = FastAPI(title="Track 03 Event Command Center", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
store = create_store()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_source": store.mode}


def _load(event_id: str) -> tuple[Event, list[OperationItem], list]:
    try:
        event, items, tasks = store.load()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not read event data: {exc}") from exc
    if event.id != event_id:
        raise HTTPException(status_code=404, detail="Event not found")
    return event, items, tasks


@app.get("/api/events/{event_id}/board")
def board(event_id: str, role: Role = "Operations") -> dict:
    event, items, tasks = _load(event_id)
    visible = [item for item in items if item.owner_role == role]
    return {
        "event": event,
        "role": role,
        "items": visible,
        "all_items": items,
        "counts": {
            "total": len(items),
            "visible": len(visible),
            "blocked": sum(item.status.casefold() == "blocked" for item in items),
            "at_risk": sum(item.status.casefold() == "at risk" for item in items),
            "tasks": len(tasks),
        },
        "role_counts": {
            selected_role: sum(item.owner_role == selected_role for item in items)
            for selected_role in ("Operations", "Volunteers", "Leadership")
        },
        "tasks": tasks,
        "data_source": store.mode,
    }


@app.post("/api/events/{event_id}/preview", response_model=ImpactResult)
def preview(event_id: str, request: ChangeRequest) -> ImpactResult:
    event, items, _ = _load(event_id)
    try:
        return evaluate_change(event, items, request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/events/{event_id}/apply", response_model=ImpactResult)
def apply(event_id: str, request: ChangeRequest) -> ImpactResult:
    result = preview(event_id, request)
    try:
        store.apply(result)
    except Exception as exc:
        # Notion may have accepted an earlier write in a multi-record operation.
        raise HTTPException(status_code=502, detail=f"Change may be partially saved; read back in Notion: {exc}") from exc
    return result


@app.post("/api/demo/reset")
def reset_demo() -> dict[str, str]:
    if store.mode != "fixtures":
        raise HTTPException(status_code=409, detail="Reset is available only in fixture mode")
    store.reset()
    return {"status": "reset", "data_source": store.mode}


@app.post("/api/events/{event_id}/closeout")
def closeout(event_id: str, request: EventCloseoutRequest) -> dict[str, str]:
    _load(event_id)
    try:
        store.closeout(event_id, request.summary.strip(), request.lessons.strip())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not save event closeout: {exc}") from exc
    return {"status": "Done", "data_source": store.mode}
