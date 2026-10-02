"""Deterministic impact analysis for event venue, schedule, and deployment changes."""

from contracts.models import (
    ChangeRequest,
    Event,
    FollowUpTask,
    ImpactedItem,
    ImpactResult,
    OperationItem,
)


def evaluate_change(
    event: Event, items: list[OperationItem], request: ChangeRequest
) -> ImpactResult:
    """Find directly affected records and walk their downstream dependencies."""
    by_id = {item.id: item for item in items}
    new_value = request.value()
    if len(new_value) < 2:
        raise ValueError("Enter a new value for this change")

    if request.change_type == "venue":
        from_value = event.venue
        roots = {
            item.id for item in items
            if item.event_id == event.id
            and item.location.casefold() == event.venue.casefold()
        }
    elif request.change_type == "schedule":
        from_value = event.date or "Unscheduled"
        if new_value == from_value:
            raise ValueError("Choose a date different from the current event date")
        # Sessions are direct schedule dependents; linked gear, volunteers, and
        # communications are included by following the same dependency graph.
        roots = {
            item.id for item in items
            if item.event_id == event.id and item.type.casefold() == "session"
        }
    else:
        from_value = ""
        target = by_id.get(request.target_item_id or "")
        if target is None or target.event_id != event.id:
            raise ValueError("Choose a volunteer or equipment record from this event")
        if target.type.casefold() not in {"volunteer", "equipment"}:
            raise ValueError("Deployment changes apply to volunteers or equipment")
        from_value = target.location
        if new_value.casefold() == from_value.casefold():
            raise ValueError("Choose a different deployment location")
        roots = {target.id}

    if not roots:
        raise ValueError("No event records match this change")

    impacted_paths: dict[str, list[str]] = {item_id: [item_id] for item_id in roots}
    changed = True
    while changed:
        changed = False
        for item in items:
            if item.event_id != event.id or item.id in impacted_paths:
                continue
            cause = next((dep for dep in item.depends_on if dep in impacted_paths), None)
            if cause:
                impacted_paths[item.id] = [item.id, *impacted_paths[cause]]
                changed = True

    noun = {
        "venue": "venue change",
        "schedule": "schedule change",
        "deployment": "deployment change",
    }[request.change_type]
    affected: list[ImpactedItem] = []
    tasks: list[FollowUpTask] = []
    for item_id in sorted(impacted_paths):
        item = by_id[item_id]
        path = impacted_paths[item_id]
        reason = (
            f"Directly affected by the {noun}: {from_value} → {new_value}."
            if len(path) == 1
            else f"Depends on {' → '.join(path[1:])}, which is affected by the {noun}."
        )
        affected.append(ImpactedItem(
            id=item.id, name=item.name, type=item.type,
            owner_role=item.owner_role, reason=reason, dependency_path=path,
        ))
        safe_value = "".join(ch if ch.isalnum() else "-" for ch in new_value).strip("-")[:16]
        task_id = f"FU-{event.id}-{request.change_type.upper()}-{item.id}-{safe_value}"
        tasks.append(FollowUpTask(
            id=task_id,
            name=f"Confirm {item.name} after {noun}: {new_value}",
            event_id=event.id,
            related_item_id=item.id,
            owner_role=item.owner_role,
        ))

    return ImpactResult(
        event_id=event.id,
        from_venue=from_value,
        to_venue=new_value,
        change_type=request.change_type,
        from_value=from_value,
        to_value=new_value,
        target_item_id=request.target_item_id,
        affected=affected,
        follow_up_tasks=tasks,
    )


def evaluate_venue_change(
    event: Event, items: list[OperationItem], new_venue: str
) -> ImpactResult:
    """Compatibility wrapper for existing venue-only callers."""
    return evaluate_change(
        event, items, ChangeRequest(change_type="venue", new_venue=new_venue)
    )
