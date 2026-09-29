from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_catalog import load_catalog  # noqa: E402
from build_entity import build_entity_view  # noqa: E402
from build_graph import build_graph  # noqa: E402


def load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


class GeneratedViewsTest(unittest.TestCase):
    def test_catalog_is_schema_valid_and_deterministically_sorted(self) -> None:
        payload = load_catalog()
        Draft202012Validator(load_schema("catalog-view.schema.json")).validate(payload)
        keys = [(record["type"], record["id"]) for record in payload["records"]]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(sum(payload["counts"].values()), len(payload["records"]))

    def test_core_graph_is_schema_valid_and_edges_have_nodes(self) -> None:
        payload = build_graph("core")
        Draft202012Validator(load_schema("graph-view.schema.json")).validate(payload)
        node_ids = {node["id"] for node in payload["nodes"]}
        self.assertEqual(payload["counts"]["nodes"], len(payload["nodes"]))
        self.assertEqual(payload["counts"]["edges"], len(payload["edges"]))
        for edge in payload["edges"]:
            self.assertIn(edge["subject"], node_ids)
            self.assertIn(edge["object"], node_ids)

    def test_all_graph_keeps_every_relationship_edge(self) -> None:
        payload = build_graph("all")
        Draft202012Validator(load_schema("graph-view.schema.json")).validate(payload)
        self.assertEqual(payload["counts"]["omitted_edges"], 0)

    def test_release_entity_view_materializes_variants_and_products(self) -> None:
        payload = build_entity_view("release:gpt-5.6")
        Draft202012Validator(load_schema("entity-view.schema.json")).validate(payload)
        variant_ids = {item["entity"]["id"] for item in payload["variants"]}
        self.assertTrue(
            {"variant:gpt-5.6-sol", "variant:gpt-5.6-terra", "variant:gpt-5.6-luna"}.issubset(variant_ids)
        )
        product_ids = {item["id"] for item in payload["related_products"]}
        self.assertIn("product:gpt-5.6-ultra", product_ids)

    def test_unknown_entity_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            build_entity_view("release:not-a-real-model")


if __name__ == "__main__":
    unittest.main()
