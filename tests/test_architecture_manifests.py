from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import records  # noqa: E402
import validate as corpus_validate  # noqa: E402


class ArchitectureManifestTests(unittest.TestCase):
    def load_schema(self) -> dict:
        return json.loads(
            (ROOT / "schemas" / "architecture.schema.json").read_text(encoding="utf-8")
        )

    def assert_schema_invalid(self, instance: dict) -> None:
        validator = Draft202012Validator(
            self.load_schema(), format_checker=FormatChecker()
        )
        self.assertTrue(list(validator.iter_errors(instance)))

    def record_index(self, *records_to_index: dict) -> dict:
        return {
            record["id"]: (Path(f"{index}.yaml"), record)
            for index, record in enumerate(records_to_index)
        }

    def minimal_architecture(self) -> dict:
        return {
            "id": "arch:example",
            "type": "architecture_spec",
            "name": "Example architecture",
            "target": "release:example",
            "status": "reviewed",
            "topology": {"type": "decoder_only"},
            "evidence": [
                {
                    "source": "source:example",
                    "locator": "Architecture section",
                    "fields": ["topology.type"],
                }
            ],
        }

    def test_schema_requires_target_status_and_evidence(self) -> None:
        architecture = self.minimal_architecture()
        for field in ("target", "status", "evidence"):
            invalid = dict(architecture)
            invalid.pop(field)
            with self.subTest(field=field):
                self.assert_schema_invalid(invalid)

    def test_schema_rejects_non_fact_evidence_path(self) -> None:
        architecture = self.minimal_architecture()
        architecture["evidence"][0]["fields"] = ["notes"]
        self.assert_schema_invalid(architecture)

    def test_schema_supports_gemma_pre_and_post_norm(self) -> None:
        architecture = self.minimal_architecture()
        architecture["topology"] = {
            "type": "decoder_only",
            "pre_norm": True,
            "post_norm": True,
        }
        architecture["evidence"][0]["fields"] = [
            "topology.type",
            "topology.pre_norm",
            "topology.post_norm",
        ]
        validator = Draft202012Validator(
            self.load_schema(), format_checker=FormatChecker()
        )
        self.assertEqual(list(validator.iter_errors(architecture)), [])

    def test_architecture_target_must_resolve_to_model(self) -> None:
        architecture = self.minimal_architecture()
        index = self.record_index(
            {"id": "release:example", "type": "technique"},
            {"id": "source:example", "type": "source"},
        )
        errors = corpus_validate.architecture_record_errors(architecture, index)
        self.assertTrue(any("must reference a model_release or model_variant" in e for e in errors))

    def test_populated_fact_requires_evidence(self) -> None:
        architecture = self.minimal_architecture()
        architecture["dimensions"] = {"layers": 32}
        index = self.record_index(
            {"id": "release:example", "type": "model_release"},
            {"id": "source:example", "type": "source"},
        )
        errors = corpus_validate.architecture_record_errors(architecture, index)
        self.assertIn("architecture field 'dimensions.layers' is missing evidence", errors)

    def test_evidence_cannot_name_an_absent_or_null_fact(self) -> None:
        architecture = self.minimal_architecture()
        architecture["attention"] = {"kv_heads": None}
        architecture["evidence"][0]["fields"].append("attention.kv_heads")
        index = self.record_index(
            {"id": "release:example", "type": "model_release"},
            {"id": "source:example", "type": "source"},
        )
        errors = corpus_validate.architecture_record_errors(architecture, index)
        self.assertTrue(any("does not name a populated architecture fact" in e for e in errors))

    def test_invalid_source_does_not_satisfy_field_coverage(self) -> None:
        architecture = self.minimal_architecture()
        index = self.record_index(
            {"id": "release:example", "type": "model_release"},
            {"id": "source:example", "type": "paper"},
        )
        errors = corpus_validate.architecture_record_errors(architecture, index)
        self.assertTrue(any("must reference type 'source'" in e for e in errors))
        self.assertIn("architecture field 'topology.type' is missing evidence", errors)

    def test_packaging_dependent_kv_heads_can_be_omitted(self) -> None:
        architecture = self.minimal_architecture()
        architecture["attention"] = {"query_heads": 128}
        architecture["evidence"][0]["fields"].append("attention.query_heads")
        index = self.record_index(
            {"id": "release:example", "type": "model_release"},
            {"id": "source:example", "type": "source"},
        )
        self.assertEqual(
            corpus_validate.architecture_record_errors(architecture, index), []
        )

    def test_block_ranges_must_be_ordered_non_overlapping_and_in_bounds(self) -> None:
        architecture = self.minimal_architecture()
        architecture["dimensions"] = {"layers": 4}
        architecture["blocks"] = [
            {"range": [0, 2]},
            {"range": [2, 4]},
            {"range": [3, 1]},
        ]
        architecture["evidence"][0]["fields"].extend(
            ["dimensions.layers", "blocks"]
        )
        index = self.record_index(
            {"id": "release:example", "type": "model_release"},
            {"id": "source:example", "type": "source"},
        )
        errors = corpus_validate.architecture_record_errors(architecture, index)
        self.assertTrue(any("overlaps" in e for e in errors))
        self.assertTrue(any("outside dimensions.layers=4" in e for e in errors))
        self.assertTrue(any("exceeds end" in e for e in errors))

    def test_repository_architectures_have_complete_field_evidence(self) -> None:
        loaded = list(records.iter_records(ROOT / "data"))
        index = {
            record["id"]: (path, record)
            for path, record in loaded
            if isinstance(record.get("id"), str)
        }
        architectures = [
            record for _, record in loaded if record.get("type") == "architecture_spec"
        ]
        self.assertGreaterEqual(len(architectures), 4)
        for architecture in architectures:
            with self.subTest(architecture=architecture["id"]):
                self.assertEqual(
                    corpus_validate.architecture_record_errors(architecture, index), []
                )

    def test_llama_405b_manifest_omits_packaging_dependent_kv_heads(self) -> None:
        llama = records.load_document(
            ROOT / "data" / "architectures" / "llama-3.1-405b.yaml"
        )
        self.assertNotIn("kv_heads", llama.get("attention", {}))
        self.assertIn("packaging-dependent", llama.get("notes", ""))


if __name__ == "__main__":
    unittest.main()
