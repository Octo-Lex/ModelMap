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

CONCEPTUAL_PREDECESSOR_CLAIM_PREDICATES = {
    "variant_of_technique",
    "generalizes",
    "extends",
}

ARCHITECTURE_FACT_SECTIONS = (
    "topology",
    "dimensions",
    "tokenization",
    "context",
    "components",
    "attention",
    "feed_forward",
    "modalities",
)


def load_schema(name: str) -> dict[str, Any]:
    with (SCHEMAS / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def claim_supports_relationship(relationship: dict[str, Any], claim: dict[str, Any]) -> bool:
    """Return whether a cited claim supports the relationship's predicate and endpoints.

    Most materialized relationships require the supporting claim to use the same
    subject, predicate, and object. Conceptual-predecessor relationships are the
    deliberate exception: the edge is oriented predecessor -> successor while the
    source claim is written from the successor's perspective using a small explicit
    vocabulary such as `variant_of_technique`, `generalizes`, or `extends`.
    """
    relationship_subject = relationship.get("subject")
    relationship_object = relationship.get("object")
    relationship_predicate = relationship.get("predicate")

    if relationship_predicate == "conceptual_predecessor_of":
        return (
            claim.get("subject") == relationship_object
            and claim.get("object") == relationship_subject
            and claim.get("predicate") in CONCEPTUAL_PREDECESSOR_CLAIM_PREDICATES
        )

    return (
        claim.get("subject") == relationship_subject
        and claim.get("object") == relationship_object
        and claim.get("predicate") == relationship_predicate
    )


def architecture_fact_paths(record: dict[str, Any]) -> set[str]:
    """Return populated architecture fact paths that require field-level evidence."""
    fields: set[str] = set()
    for section in ARCHITECTURE_FACT_SECTIONS:
        value = record.get(section)
        if not isinstance(value, dict):
            continue
        for key, field_value in value.items():
            if field_value is not None:
                fields.add(f"{section}.{key}")

    # A heterogeneous layer plan is evidenced as one atomic fact. Per-block notes
    # and properties remain covered by the evidence attached to the full plan.
    if record.get("blocks") is not None:
        fields.add("blocks")
    return fields


def architecture_record_errors(
    record: dict[str, Any],
    by_id: dict[str, tuple[Path, dict[str, Any]]],
) -> list[str]:
    """Validate architecture targets, field evidence, and block-plan invariants."""
    messages: list[str] = []

    target_ref = record.get("target")
    target = by_id.get(target_ref) if isinstance(target_ref, str) else None
    if target is None:
        messages.append(f"unresolved architecture target {target_ref!r}")
    elif target[1].get("type") not in {"model_release", "model_variant"}:
        messages.append(
            f"architecture target {target_ref!r} must reference a model_release "
            f"or model_variant, found {target[1].get('type')!r}"
        )

    fact_paths = architecture_fact_paths(record)
    covered_fields: set[str] = set()
    for evidence in record.get("evidence", []):
        if not isinstance(evidence, dict):
            continue

        source_ref = evidence.get("source")
        source = by_id.get(source_ref) if isinstance(source_ref, str) else None
        source_is_valid = source is not None and source[1].get("type") == "source"
        if source is None:
            messages.append(f"unresolved architecture evidence source {source_ref!r}")
        elif not source_is_valid:
            messages.append(
                f"architecture evidence {source_ref!r} must reference type 'source', "
                f"found {source[1].get('type')!r}"
            )

        fields = evidence.get("fields", [])
        if not isinstance(fields, list):
            continue
        for field in fields:
            if not isinstance(field, str):
                continue
            if field not in fact_paths:
                messages.append(
                    f"architecture evidence field {field!r} does not name a populated "
                    "architecture fact"
                )
            elif source_is_valid:
                covered_fields.add(field)

    for field in sorted(fact_paths - covered_fields):
        messages.append(f"architecture field {field!r} is missing evidence")

    blocks = record.get("blocks")
    dimensions = record.get("dimensions")
    layer_count = None
    if isinstance(dimensions, dict) and type(dimensions.get("layers")) is int:
        layer_count = dimensions["layers"]

    valid_ranges: list[tuple[int, int, int]] = []
    if isinstance(blocks, list):
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            block_range = block.get("range")
            if not (
                isinstance(block_range, list)
                and len(block_range) == 2
                and all(type(value) is int for value in block_range)
            ):
                continue

            start, end = block_range
            if start > end:
                messages.append(
                    f"blocks[{index}].range start {start} exceeds end {end}"
                )
                continue
            if layer_count is not None and end >= layer_count:
                messages.append(
                    f"blocks[{index}].range end {end} is outside "
                    f"dimensions.layers={layer_count}"
                )

            for previous_index, previous_start, previous_end in valid_ranges:
                if start <= previous_end and previous_start <= end:
                    messages.append(
                        f"blocks[{index}].range [{start}, {end}] overlaps "
                        f"blocks[{previous_index}].range "
                        f"[{previous_start}, {previous_end}]"
                    )
            valid_ranges.append((index, start, end))

    return messages


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
        validator = Draft202012Validator(
            schema_cache[schema_name], format_checker=FormatChecker()
        )
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
                        f"predicate/endpoints {record.get('subject')!r} "
                        f"-{record.get('predicate')}-> {record.get('object')!r}"
                    )
        elif record_type == "architecture_spec":
            rel = path.relative_to(ROOT)
            for message in architecture_record_errors(record, by_id):
                errors.append(f"{rel}: {message}")
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
