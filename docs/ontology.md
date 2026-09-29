# Canonical ontology v0.1

ModelMap stores historical and technical knowledge as versioned entities connected by evidence-backed claims and typed relationships.

## 1. Entity classes

### ModelFamily
A long-lived lineage or branded research family, such as a sequence of related model generations.

### ModelRelease
A named generation or release within a family.

### ModelVariant
A concrete checkpoint, API variant, instruct/base variant, reasoning variant, or other materially distinct model artifact.

### ArchitectureSpec
A structural description of a model: topology, attention, positional encoding, normalization, FFN/MoE structure, layer plan, context mechanics, and related architectural properties.

### Technique
A reusable technical mechanism or method, such as grouped-query attention, multi-head latent attention, rotary embeddings, sparse MoE routing, multi-token prediction, quantization, or a post-training method.

### TrainingRun
A pretraining, continued-training, post-training, distillation, or reinforcement-learning process that produces or changes a model artifact.

### Implementation
Code that implements a model or technique. Fidelity is classified separately as educational, reference, or verified.

### Paper
A scholarly or technical publication that may introduce, describe, analyze, or evaluate models and techniques.

### Source
Any evidentiary artifact: paper, technical report, model card, official repository/config, announcement, benchmark report, dataset card, or independent reproduction.

### Claim
An atomic assertion about a subject, predicate, and object/value, accompanied by evidence and an evidence state.

### Relationship
A typed graph edge between canonical entities. Relationships represent graph structure; claims represent evidence-backed assertions. A relationship may be materialized from one or more accepted claims.

### Event
A historical occurrence with an event time distinct from source publication time: announcement, weights release, API launch, paper publication, license change, benchmark publication, deprecation, and similar events.

### Dataset / DatasetVersion
A named data asset and a specific revision or release of that asset.

### Benchmark / BenchmarkVersion
An evaluation task and a specific version of that task.

### EvaluationProtocol
The conditions under which a benchmark is run: prompt, shot count, sampling settings, tools, reasoning budget, aggregation, scoring, and evaluator implementation.

### EvaluationRun
A concrete execution of a model on a benchmark under an evaluation protocol.

### Organization / Person
Institutions and people involved in model development, publication, evaluation, or infrastructure.

### License
Distribution or use terms for weights, code, or data.

### HardwareSystem
A training or inference hardware/system configuration distinct from the model architecture itself.

### ProductSystem
A user-facing or API system built around one or more models. Product routing and orchestration must not be conflated with a single model architecture.

## 2. Stable identifiers

Canonical IDs use a namespace and a stable slug:

```text
family:deepseek
release:deepseek-v3
variant:deepseek-v3-base
technique:multi-head-latent-attention
org:deepseek
paper:arxiv-2412-19437
benchmark:mmlu
```

Namespaces are bound to entity types. The v0.1 mapping is:

| Entity type | Namespace |
|---|---|
| model_family | `family:` |
| model_release | `release:` |
| model_variant | `variant:` |
| architecture_spec | `arch:` |
| technique | `technique:` |
| training_run | `training:` |
| implementation | `implementation:` |
| paper | `paper:` |
| source | `source:` |
| claim | `claim:` |
| relationship | `relationship:` |
| event | `event:` |
| dataset | `dataset:` |
| dataset_version | `dataset-version:` |
| benchmark | `benchmark:` |
| benchmark_version | `benchmark-version:` |
| evaluation_protocol | `eval-protocol:` |
| evaluation_run | `eval-run:` |
| organization | `org:` |
| person | `person:` |
| license | `license:` |
| hardware_system | `hardware:` |
| product_system | `product:` |

Display names and aliases are mutable metadata, not primary keys.

## 3. Claim model

A claim is the smallest independently supportable assertion.

```yaml
id: claim:example-model-uses-gqa
type: claim
subject: release:example-model
predicate: uses_technique
object: technique:grouped-query-attention
status: confirmed_primary
evidence:
  - source: source:example-technical-report
valid_from: '2025-01-01'
```

Claims may point to entities (`object`) or literal values (`value`), but not both simultaneously. Claim and relationship endpoints must use canonical IDs, never display names.

## 4. Evidence states

- `confirmed_primary`: explicitly documented by authoritative primary material.
- `reported_primary`: claimed by the developer/vendor but not independently reproduced.
- `independently_verified`: reproduced or confirmed by an independent source.
- `inferred`: technical inference not explicitly disclosed.
- `disputed`: credible sources conflict.
- `superseded`: historically correct but no longer current.
- `unknown`: the public record does not establish the value.

Confidence numbers are intentionally avoided in v0.1. Evidence class and source quality are more interpretable than arbitrary scalar confidence.

## 5. Relationship vocabulary

Core predicates include:

- `release_of`
- `variant_of`
- `succeeds`
- `checkpoint_derived_from`
- `fine_tuned_from`
- `distilled_from`
- `uses_architecture`
- `uses_technique`
- `introduces_technique`
- `implements`
- `trained_on`
- `evaluated_on`
- `published_by`
- `authored_by`
- `supports_modality`
- `supports_claim`
- `contradicts_claim`
- `replaces`

Subjective predicates such as `inspired_by`, `influenced`, or `popularized` require explicit historical evidence and should not be inferred from temporal proximity or architectural similarity alone.

## 6. Two different kinds of lineage

### Parameter lineage
Concrete descent of weights or training state:

```text
checkpoint A → fine-tuned → checkpoint B → distilled → checkpoint C
```

### Conceptual lineage
Evolution or adoption of ideas:

```text
MHA → MQA → GQA → low-rank KV compression → MLA
```

These use different edge types. Conceptual similarity must never imply checkpoint ancestry.

## 7. Architecture representation

Architecture records should support heterogeneous layer plans rather than assuming every block is identical.

```yaml
blocks:
  - range: [0, 2]
    attention: component:mla
    ffn: component:dense-swiglu
  - range: [3, 60]
    attention: component:mla
    ffn: component:sparse-moe
```

Unknown values are represented as `null`; `null` does not mean zero or not applicable.

## 8. Evaluation ontology

Benchmark results are only meaningful together with their protocol.

```text
Benchmark → BenchmarkVersion → EvaluationProtocol → EvaluationRun → Result
```

Protocols should capture at least the information needed to distinguish zero/few-shot settings, chain-of-thought or direct answering, tool use, reasoning budget, sampling multiplicity, aggregation method, scoring metric, and evaluator implementation.

The UI should warn when two displayed results use materially different protocols.

## 9. Temporal model

`occurred_at` belongs to an Event. `published_at` belongs to a Source. `retrieved_at` records when ModelMap observed a source. These dates are intentionally separate.

Quote dates in hand-authored YAML for readability and portability. The validator also normalizes YAML date/timestamp scalars to ISO strings before applying JSON Schema.

## 10. Source hierarchy

Preferred evidence order for technical claims:

1. paper / technical report;
2. official model card;
3. official repository and configuration;
4. official release or engineering note;
5. independent reproduction;
6. high-quality secondary technical analysis;
7. community discussion as discovery evidence, not canonical technical authority.

## 11. Editorial invariant

Canonical factual assertions require evidence unless explicitly represented as `inferred` or `unknown`.

The ingestion pipeline should therefore be:

```text
source → candidate claims → normalization → schema validation → human review → canonical corpus
```
