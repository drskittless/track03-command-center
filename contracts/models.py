"""Shared API contracts for the event command center."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Role = Literal["Operations", "Volunteers", "Leadership"]


class Event(BaseModel):
    id: str
    name: str
    venue: str
    date: str | None = None
    status: str = "Planned"


class OperationItem(BaseModel):
    id: str
    name: str
    event_id: str
    type: str
    owner_role: Role
    status: str
    location: str
    depends_on: list[str] = Field(default_factory=list)
    dependency_reason: str = ""


class ImpactedItem(BaseModel):
    id: str
    name: str
    type: str
    owner_role: Role
    reason: str
    dependency_path: list[str]


class FollowUpTask(BaseModel):
    id: str
    name: str
    event_id: str
    related_item_id: str
    owner_role: Role
    status: str = "Todo"


class ImpactResult(BaseModel):
    event_id: str
    from_venue: str
    to_venue: str
    change_type: Literal["venue", "schedule", "deployment"] = "venue"
    from_value: str = ""
    to_value: str = ""
    target_item_id: str | None = None
    affected: list[ImpactedItem]
    follow_up_tasks: list[FollowUpTask]


class ChangeRequest(BaseModel):
    change_type: Literal["venue", "schedule", "deployment"] = "venue"
    new_venue: str | None = Field(default=None, min_length=2, max_length=120)
    new_date: str | None = Field(default=None, min_length=8, max_length=32)
    target_item_id: str | None = None
    new_location: str | None = Field(default=None, min_length=2, max_length=120)

    @model_validator(mode="after")
    def validate_change_fields(self) -> "ChangeRequest":
        if self.change_type == "venue" and not self.new_venue:
            raise ValueError("new_venue is required for a venue change")
        if self.change_type == "schedule":
            if not self.new_date:
                raise ValueError("new_date is required for a schedule change")
            date.fromisoformat(self.new_date)
        if self.change_type == "deployment" and (not self.target_item_id or not self.new_location):
            raise ValueError("target_item_id and new_location are required for a deployment change")
        return self

    def value(self) -> str:
        if self.change_type == "venue":
            return (self.new_venue or "").strip()
        if self.change_type == "schedule":
            return (self.new_date or "").strip()
        return (self.new_location or "").strip()


# Kept as an import alias for the original venue-only client contract.
VenueChangeRequest = ChangeRequest


class EventCloseoutRequest(BaseModel):
    summary: str = Field(min_length=5, max_length=1500)
    lessons: str = Field(min_length=5, max_length=1500)
