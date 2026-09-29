#!/usr/bin/env python3
"""Build a deterministic browse catalog from canonical ModelMap records."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from records import iter_records

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CATALOG_TYPES = {
    "architecture_spec",
    "benchmark",
    "benchmark_version",
    "dataset",
    "dataset_version",
    "evaluation_protocol",
    "evaluation_run",
    "hardware_system",
    "implementation",
    "license",
    "model_family",
    "model_release",
    "model_variant",
    "organization",
    "paper",
    "person",
    "product_system",
    "technique",
    "training_run",
}


def load_catalog(record_type: str | None = None) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path, record in iter_records(DATA):
        rtype = record.get("type")
        if rtype not in CATALOG_TYPES:
            continue
        if record_type and rtype != record_type:
            continue
        item = dict(record)
        item["record_path"] = path.relative_to(ROOT).as_posix()
        records.append(item)

    records.sort(key=lambda item: (str(item.get("type", "")), str(item["id"])))
    counts = Counter(str(item["type"]) for item in records)
    return {
        "generated_from": "canonical-records",
        "filter_type": record_type,
        "counts": dict(sorted(counts.items())),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", dest="record_type", choices=sorted(CATALOG_TYPES))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = load_catalog(args.record_type)
    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
