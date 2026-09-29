"""Shared canonical-record loading utilities for ModelMap tools."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

import yaml

SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}


def normalize_scalars(value: Any) -> Any:
    """Convert YAML-native date/time objects to JSON-compatible ISO strings."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [normalize_scalars(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_scalars(item) for key, item in value.items()}
    return value


def load_document(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        if path.suffix == ".json":
            document = json.load(fh)
        else:
            document = yaml.safe_load(fh)
    return normalize_scalars(document)


def iter_record_paths(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS:
            yield path


def iter_records(root: Path) -> Iterator[tuple[Path, dict[str, Any]]]:
    for path in iter_record_paths(root):
        document = load_document(path)
        if not isinstance(document, dict):
            raise ValueError(f"{path} must contain exactly one mapping/object record")
        yield path, document
