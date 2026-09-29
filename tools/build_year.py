#!/usr/bin/env python3
"""Render a single year from ModelMap canonical event records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "events"


def load_events(year: int) -> list[dict]:
    out = []
    for path in sorted(EVENTS.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as fh:
            event = yaml.safe_load(fh)
        if str(event.get("occurred_at", "")).startswith(f"{year:04d}-"):
            out.append(event)
    return sorted(out, key=lambda e: (e["occurred_at"], e["id"]))


def render_markdown(year: int, events: list[dict]) -> str:
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
        print(json.dumps({"year": args.year, "events": events}, indent=2))
    else:
        print(render_markdown(args.year, events), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
