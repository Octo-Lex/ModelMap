#!/usr/bin/env python3
"""Build a read-model payload for one canonical ModelMap entity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from records import iter_records

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_index() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    index: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for path, record in iter_records(DATA):
        item = dict(record)
        item["record_path"] = path.relative_to(ROOT).as_posix()
        records.append(item)
        if item.get("id"):
            index[str(item["id"])] = item
    return index, records


def build_entity_view(entity_id: str) -> dict[str, Any]:
    index, records = load_index()
    if entity_id not in index:
        raise KeyError(f"Unknown canonical id: {entity_id}")

    outgoing = sorted(
        [r for r in records if r.get("type") == "relationship" and r.get("subject") == entity_id],
        key=lambda r: r["id"],
    )
    incoming = sorted(
        [r for r in records if r.get("type") == "relationship" and r.get("object") == entity_id],
        key=lambda r: r["id"],
    )
    claims = sorted(
        [r for r in records if r.get("type") == "claim" and r.get("subject") == entity_id],
        key=lambda r: r["id"],
    )
    events = sorted(
        [r for r in records if r.get("type") == "event" and r.get("subject") == entity_id],
        key=lambda r: (str(r.get("occurred_at", "")), r["id"]),
    )

    variant_ids = sorted(
        r["subject"]
        for r in incoming
        if r.get("predicate") == "variant_of" and str(r.get("subject", "")).startswith("variant:")
    )
    variants: list[dict[str, Any]] = []
    for variant_id in variant_ids:
        variant = index.get(variant_id)
        if not variant:
            continue
        variant_claims = sorted(
            [r for r in records if r.get("type") == "claim" and r.get("subject") == variant_id],
            key=lambda r: r["id"],
        )
        variant_events = sorted(
            [r for r in records if r.get("type") == "event" and r.get("subject") == variant_id],
            key=lambda r: (str(r.get("occurred_at", "")), r["id"]),
        )
        variants.append({"entity": variant, "claims": variant_claims, "events": variant_events})

    related_products = sorted(
        [
            r
            for r in records
            if r.get("type") == "product_system"
            and isinstance(r.get("metadata"), dict)
            and r["metadata"].get("model_release") == entity_id
        ],
        key=lambda r: r["id"],
    )

    return {
        "generated_from": "canonical-records",
        "entity": index[entity_id],
        "outgoing_relationships": outgoing,
        "incoming_relationships": incoming,
        "claims": claims,
        "events": events,
        "variants": variants,
        "related_products": related_products,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("entity_id")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    try:
        payload = build_entity_view(args.entity_id)
    except KeyError as exc:
        parser.error(str(exc))
    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
