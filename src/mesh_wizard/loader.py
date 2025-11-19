"""Loading utilities for mesh topology files."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .model import MeshTopology
from .schema_validator import validate_dict


def _load_single_file(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Mesh file {path} must be a mapping at the top level")
    return data


def _merge_dict(base: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in new_data.items():
        if key in base and isinstance(base[key], list) and isinstance(value, list):
            base[key].extend(value)
        elif key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def load_raw(path: str | Path) -> Dict[str, Any]:
    path_obj = Path(path)
    if path_obj.is_file():
        data = _load_single_file(path_obj)
    elif path_obj.is_dir():
        data: Dict[str, Any] = {}
        for candidate in sorted(path_obj.glob("*.y*ml")):
            fragment = _load_single_file(candidate)
            data = _merge_dict(data, fragment)
    else:
        raise FileNotFoundError(path)
    validate_dict(data)
    return data


def load_topology(path: str | Path) -> MeshTopology:
    raw = load_raw(path)
    return MeshTopology.from_dict(raw)
