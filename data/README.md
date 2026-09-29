# Canonical data layout

`data/` contains ModelMap's source-of-truth records. Human-readable articles, timelines, comparison tables, graphs, and site pages should be generated from these records rather than maintaining duplicate facts.

## Directories

```text
data/
├── families/
├── releases/
├── variants/
├── architectures/
├── techniques/
├── training/
├── implementations/
├── papers/
├── sources/
├── claims/
├── relationships/
├── events/
├── organizations/
├── people/
├── datasets/
├── benchmarks/
├── evaluations/
├── licenses/
├── hardware/
├── products/
└── vocabularies/
```

Directories are introduced as canonical records are added; empty directories do not need placeholders.

## File format

Initial canonical records should be YAML where hand-editability is valuable. JSON Schema files in `/schemas` define the contracts. Validation tooling may normalize YAML to JSON internally.

Exactly one canonical record is stored per YAML/JSON file. This is a repository invariant, not merely a preference: it keeps Git diffs, provenance, review state, and correction history scoped to one stable ID.

```text
data/techniques/grouped-query-attention.yaml
data/releases/deepseek-v3.yaml
data/sources/deepseek-v3-technical-report.yaml
data/claims/deepseek-v3-uses-mla.yaml
```

Do not store arrays of claims or other multi-record containers in canonical files. Related atomic claims may share a naming prefix or directory grouping, but each retains its own file and globally unique canonical ID.

## Identifier conventions

Use lowercase namespaces and lowercase slugs:

```text
family:llama
release:llama-3.1
variant:llama-3.1-405b-instruct
arch:llama-3.1-405b
technique:grouped-query-attention
source:llama-3.1-model-card
claim:llama-3.1-uses-gqa
relationship:llama-3.1-uses-gqa
```

IDs must remain stable if display names change. Entity types are bound to canonical namespaces as documented in `docs/ontology.md`.

## Null, unknown, and not applicable

Do not overload values:

- `null` means a field has no established value in the canonical record.
- an explicit claim with status `unknown` means the public record was reviewed and does not establish the fact.
- fields that genuinely do not apply should be omitted when allowed by the schema rather than written as misleading zeros or empty strings.

## Evidence locations

Evidence references should identify a source plus the smallest useful locator available: section, table, page, config key, file/line range, release-note heading, or commit.

## Architecture manifests

An `ArchitectureSpec` targets exactly one canonical model release or model variant through `target`. Every populated architecture fact must be covered by at least one field-level evidence entry. Evidence entries identify a canonical `source`, a narrow `locator`, and the exact fact paths supported by that locator.

```yaml
id: arch:example-model
type: architecture_spec
name: Example model architecture
target: variant:example-model
status: reviewed
topology:
  type: decoder_only
attention:
  query_heads: 32
evidence:
  - source: source:example-model-report
    locator: '§2 Model Architecture, Table 1'
    fields:
      - topology.type
      - attention.query_heads
```

The validator rejects evidence paths that point to absent or `null` values and rejects populated architecture facts that lack evidence. `notes` are editorial context and are not treated as architecture facts requiring field evidence.

Layer-plan ranges in `blocks` are zero-based and inclusive. Ranges must be ordered internally, must not overlap, and must remain within `dimensions.layers` when the layer count is present.

Architecture fields whose values are unestablished or vary by checkpoint packaging within the manifest's target should be omitted rather than guessed, averaged, or selected from one package and presented as intrinsic architecture. Use `null` only when preserving an explicit reviewed-but-unestablished slot is itself useful to the record.

## Dates and timestamps

Quote ISO dates and timestamps in hand-authored YAML when practical. The shared record loader normalizes YAML-native `date` and `datetime` scalars to ISO strings before schema validation and generation, so equivalent unquoted YAML remains valid.

## Review policy

A record may move through:

```text
draft → reviewed → canonical
```

Canonical status means the record meets the current schema and evidence policy; it does not mean the record can never be corrected. Corrections are expected to remain auditable through Git history.

## Initial ingestion order

The first historical backbone should establish:

1. foundational techniques and papers needed to explain later models;
2. core 2023 model families and architectural transitions;
3. high-resolution 2024–present releases;
4. benchmark/evaluation protocols only when needed to support model comparisons;
5. executable primitives after their canonical technique records exist.
