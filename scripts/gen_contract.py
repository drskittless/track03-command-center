"""Write deterministic JSON Schema and OpenAPI contract snapshots."""

import inspect
import json
from pathlib import Path

from pydantic import BaseModel

from apps.api.app.main import app
from contracts import models


def write_json(path: str, data: object) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


schemas = {
    name: model.model_json_schema()
    for name, model in inspect.getmembers(models, inspect.isclass)
    if issubclass(model, BaseModel)
    and model is not BaseModel
    and model.__module__ == models.__name__
}
write_json("contracts/schema.json", schemas)
write_json("contracts/openapi.json", app.openapi())
