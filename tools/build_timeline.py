#!/usr/bin/env python3
"""Render ModelMap event records as a chronologically sorted timeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "events"


def load_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not EVENTS.exists():
        return events
    for path in sorted(EVENTS.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as fh:
            record = yaml.safe_load(fh)
        if not isinstance(record, dict) or record.get("type") != "event":
            continue
        events.append(record)
    return sorted(events, key=lambda item: (item["occurred_at"], item["id"]))


def render_markdown(events: list[dict[str, Any]]) -> str:
    lines = ["# ModelMap timeline", "", "| Date | Event | Type | Subject |", "|---|---|---|---|"]
    for event in events:
        lines.append(
            f"| {event['occurred_at']} | {event['name']} | {event['event_type']} | `{event['subject']}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    events = load_events()
    if args.format == "markdown":
        rendered = render_markdown(events)
    else:
        rendered = json.dumps(events, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
