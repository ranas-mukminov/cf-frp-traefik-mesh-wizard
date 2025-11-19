"""Validate mesh YAML files."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import jsonschema
import yaml

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "mesh-schema.yaml"


def _load_schema() -> Dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def _compiled_validator() -> jsonschema.Draft7Validator:
    schema = _load_schema()
    return jsonschema.Draft7Validator(schema)


def validate_dict(data: Dict[str, Any]) -> None:
    """Validate dictionary raising ValueError on problems."""
    validator = _compiled_validator()
    errors = sorted(validator.iter_errors(data), key=lambda err: err.path)
    if errors:
        message = "; ".join(f"{'/'.join(map(str, error.path))}: {error.message}" for error in errors)
        raise ValueError(f"Mesh schema validation failed: {message}")
