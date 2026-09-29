from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_year  # noqa: E402
import records  # noqa: E402
import validate as corpus_validate  # noqa: E402


class ReviewHardeningTests(unittest.TestCase):
    def load_schema(self, name: str) -> dict:
        return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))

    def assert_invalid(self, schema_name: str, instance: dict) -> None:
        validator = Draft202012Validator(
            self.load_schema(schema_name), format_checker=FormatChecker()
        )
        self.assertTrue(list(validator.iter_errors(instance)))

    def test_yaml_dates_are_normalized_to_strings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.yaml"
            path.write_text("occurred_at: 2025-01-01\n", encoding="utf-8")
            loaded = records.load_document(path)
        self.assertEqual(loaded["occurred_at"], "2025-01-01")
        self.assertIsInstance(loaded["occurred_at"], str)

    def test_all_supported_extensions_are_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.yaml").write_text("id: event:a\n", encoding="utf-8")
            (root / "b.yml").write_text("id: event:b\n", encoding="utf-8")
            (root / "c.json").write_text('{"id":"event:c"}', encoding="utf-8")
            suffixes = {path.suffix for path in records.iter_record_paths(root)}
        self.assertEqual(suffixes, {".yaml", ".yml", ".json"})

    def test_claim_endpoint_requires_canonical_id(self) -> None:
        self.assert_invalid(
            "claim.schema.json",
            {
                "id": "claim:bad-endpoint",
                "type": "claim",
                "subject": "display name",
                "predicate": "uses_technique",
                "object": "technique:gqa",
                "status": "inferred",
                "evidence": [],
            },
        )

    def test_claim_endpoint_rejects_unsupported_namespace(self) -> None:
        self.assert_invalid(
            "claim.schema.json",
            {
                "id": "claim:unsupported-namespace",
                "type": "claim",
                "subject": "unsupported:anything",
                "predicate": "uses_technique",
                "object": "technique:gqa",
                "status": "inferred",
                "evidence": [],
            },
        )

    def test_relationship_endpoint_requires_canonical_id(self) -> None:
        self.assert_invalid(
            "relationship.schema.json",
            {
                "id": "relationship:bad-endpoint",
                "type": "relationship",
                "subject": "release:model",
                "predicate": "release_of",
                "object": "Family Name",
            },
        )

    def test_entity_type_is_bound_to_namespace(self) -> None:
        self.assert_invalid(
            "entity.schema.json",
            {"id": "claim:not-a-family", "type": "model_family", "name": "Example"},
        )

    def test_generated_year_payload_conforms_to_schema(self) -> None:
        event = {
            "id": "event:example",
            "type": "event",
            "name": "Example event",
            "event_type": "model_announced",
            "subject": "release:example",
            "occurred_at": "2023-01-01",
            "evidence": ["source:example"],
        }
        payload = build_year.build_payload(2023, [event])
        validator = Draft202012Validator(
            self.load_schema("year-view.schema.json"), format_checker=FormatChecker()
        )
        self.assertEqual(list(validator.iter_errors(payload)), [])

    def test_year_view_rejects_noncanonical_embedded_event(self) -> None:
        invalid_event = {
            "id": "event:example",
            "type": "event",
            "name": "Example event",
            "event_type": "typo",
            "subject": "unsupported:anything",
            "occurred_at": "2023-01-01",
            "evidence": ["source:example"],
        }
        self.assert_invalid(
            "year-view.schema.json",
            build_year.build_payload(2023, [invalid_event]),
        )

    def test_relationship_claim_endpoints_must_match(self) -> None:
        relationship = {
            "subject": "release:example",
            "predicate": "uses_technique",
            "object": "technique:gqa",
        }
        matching_claim = {
            "subject": "release:example",
            "object": "technique:gqa",
        }
        unrelated_claim = {
            "subject": "release:other",
            "object": "technique:gqa",
        }
        self.assertTrue(
            corpus_validate.claim_supports_relationship(relationship, matching_claim)
        )
        self.assertFalse(
            corpus_validate.claim_supports_relationship(relationship, unrelated_claim)
        )

    def test_conceptual_predecessor_claim_uses_reverse_endpoint_order(self) -> None:
        relationship = {
            "subject": "technique:multi-head-attention",
            "predicate": "conceptual_predecessor_of",
            "object": "technique:multi-query-attention",
        }
        successor_perspective_claim = {
            "subject": "technique:multi-query-attention",
            "object": "technique:multi-head-attention",
        }
        self.assertTrue(
            corpus_validate.claim_supports_relationship(
                relationship, successor_perspective_claim
            )
        )

    def test_canonical_file_contains_one_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "claims.yaml").write_text("- id: claim:a\n- id: claim:b\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one mapping/object record"):
                list(records.iter_records(root))


if __name__ == "__main__":
    unittest.main()
