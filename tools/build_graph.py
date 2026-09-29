#!/usr/bin/env python3
"""Build a deterministic knowledge-graph export from canonical ModelMap records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from records import iter_records
from build_catalog import CATALOG_TYPES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def label_for(record: dict[str, Any]) -> str:
    return str(record.get("name") or record.get("title") or record["id"])


def build_graph(scope: str = "core") -> dict[str, Any]:
    all_records: dict[str, tuple[Path, dict[str, Any]]] = {}
    relationships: list[dict[str, Any]] = []
    for path, record in iter_records(DATA):
        record_id = record.get("id")
        if record_id:
            all_records[str(record_id)] = (path, record)
        if record.get("type") == "relationship":
            relationships.append(record)

    if scope == "core":
        node_ids = {
            record_id
            for record_id, (_, record) in all_records.items()
            if record.get("type") in CATALOG_TYPES
        }
    else:
        node_ids = {
            record_id
            for record_id, (_, record) in all_records.items()
            if record.get("type") != "relationship"
        }

    nodes: list[dict[str, Any]] = []
    for record_id in sorted(node_ids):
        path, record = all_records[record_id]
        nodes.append(
            {
                "id": record_id,
                "type": record.get("type"),
                "label": label_for(record),
                "record_path": path.relative_to(ROOT).as_posix(),
            }
        )

    edges: list[dict[str, Any]] = []
    omitted_edges = 0
    for relation in sorted(relationships, key=lambda item: item["id"]):
        if relation["subject"] not in node_ids or relation["object"] not in node_ids:
            omitted_edges += 1
            continue
        edges.append(
            {
                "id": relation["id"],
                "subject": relation["subject"],
                "predicate": relation["predicate"],
                "object": relation["object"],
                "claim_refs": relation.get("claim_refs", []),
            }
        )

    return {
        "generated_from": "canonical-records-and-relationships",
        "scope": scope,
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "omitted_edges": omitted_edges,
        },
        "nodes": nodes,
        "edges": edges,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["core", "all"], default="core")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_graph(args.scope)
    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
