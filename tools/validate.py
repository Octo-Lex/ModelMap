#!/usr/bin/env python3
"""Validate ModelMap canonical records and cross-record references."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from records import iter_records

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas"

SCHEMA_BY_TYPE = {
    "source": "source.schema.json",
    "claim": "claim.schema.json",
    "relationship": "relationship.schema.json",
    "architecture_spec": "architecture.schema.json",
    "event": "event.schema.json",
}


def load_schema(name: str) -> dict[str, Any]:
    with (SCHEMAS / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def claim_supports_relationship(relationship: dict[str, Any], claim: dict[str, Any]) -> bool:
    """Return whether a cited claim supports the relationship's materialized endpoints.

    Conceptual predecessor relationships are intentionally oriented predecessor -> successor,
    while their source claims are written from the successor's perspective (for example,
    MQA variant_of MHA). All other relationship types require identical endpoint order.
    """
    relationship_subject = relationship.get("subject")
    relationship_object = relationship.get("object")
    if relationship.get("predicate") == "conceptual_predecessor_of":
        expected_subject, expected_object = relationship_object, relationship_subject
    else:
        expected_subject, expected_object = relationship_subject, relationship_object
    return claim.get("subject") == expected_subject and claim.get("object") == expected_object


def main() -> int:
    errors: list[str] = []
    try:
        records = list(iter_records(DATA))
    except Exception as exc:
        print(f"ERROR: failed to load corpus: {exc}")
        return 1

    schema_cache = {
        name: load_schema(name)
        for name in set(SCHEMA_BY_TYPE.values()) | {"entity.schema.json"}
    }
    by_id: dict[str, tuple[Path, dict[str, Any]]] = {}

    for path, record in records:
        rel = path.relative_to(ROOT)
        schema_name = SCHEMA_BY_TYPE.get(record.get("type"), "entity.schema.json")
        validator = Draft202012Validator(schema_cache[schema_name], format_checker=FormatChecker())
        for err in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
            location = ".".join(str(part) for part in err.path) or "<root>"
            errors.append(f"{rel}: {location}: {err.message}")
        record_id = record.get("id")
        if isinstance(record_id, str):
            if record_id in by_id:
                previous = by_id[record_id][0].relative_to(ROOT)
                errors.append(f"{rel}: duplicate id {record_id!r}; first seen in {previous}")
            else:
                by_id[record_id] = (path, record)

    def require_id(
        owner: Path, ref: Any, expected_type: str | None = None
    ) -> tuple[Path, dict[str, Any]] | None:
        rel = owner.relative_to(ROOT)
        if not isinstance(ref, str):
            errors.append(f"{rel}: reference must be a string, got {type(ref).__name__}")
            return None
        target = by_id.get(ref)
        if target is None:
            errors.append(f"{rel}: unresolved reference {ref!r}")
            return None
        if expected_type is not None and target[1].get("type") != expected_type:
            errors.append(
                f"{rel}: {ref!r} must reference type {expected_type!r}, "
                f"found {target[1].get('type')!r}"
            )
            return None
        return target

    for path, record in records:
        record_type = record.get("type")
        if record_type == "claim":
            require_id(path, record.get("subject"))
            if "object" in record:
                require_id(path, record.get("object"))
            for evidence in record.get("evidence", []):
                require_id(path, evidence.get("source"), "source")
        elif record_type == "relationship":
            require_id(path, record.get("subject"))
            require_id(path, record.get("object"))
            for claim_ref in record.get("claim_refs", []):
                claim_target = require_id(path, claim_ref, "claim")
                if claim_target is None:
                    continue
                claim = claim_target[1]
                if not claim_supports_relationship(record, claim):
                    rel = path.relative_to(ROOT)
                    errors.append(
                        f"{rel}: claim_ref {claim_ref!r} does not support relationship "
                        f"endpoints {record.get('subject')!r} -> {record.get('object')!r}"
                    )
        elif record_type == "event":
            require_id(path, record.get("subject"))
            for source_ref in record.get("evidence", []):
                require_id(path, source_ref, "source")

    if errors:
        print(f"ModelMap validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    counts: dict[str, int] = {}
    for _, record in records:
        kind = str(record.get("type", "unknown"))
        counts[kind] = counts.get(kind, 0) + 1
    summary = ", ".join(f"{kind}={count}" for kind, count in sorted(counts.items()))
    print(f"ModelMap validation passed: {len(records)} records ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
