#!/usr/bin/env python3
"""Render a single year from ModelMap canonical event records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from records import iter_records

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "events"


def load_events(year: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for _, event in iter_records(EVENTS):
        if event.get("type") != "event":
            continue
        if str(event.get("occurred_at", "")).startswith(f"{year:04d}-"):
            out.append(event)
    return sorted(out, key=lambda e: (e["occurred_at"], e["id"]))


def build_payload(year: int, events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "year": year,
        "generated_from": "canonical-events",
        "events": events,
    }


def render_markdown(year: int, events: list[dict[str, Any]]) -> str:
    lines = [f"# {year}", "", "Generated from canonical ModelMap event records.", ""]
    for event in events:
        title = event.get("name") or event["id"].split(":", 1)[-1].replace("-", " ").title()
        lines.append(f"- **{event['occurred_at']}** — {title} (`{event['event_type']}`) — `{event['subject']}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()
    events = load_events(args.year)
    if args.format == "json":
        print(json.dumps(build_payload(args.year, events), indent=2, sort_keys=True))
    else:
        print(render_markdown(args.year, events), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
