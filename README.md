# ModelMap — LLM Evolution Atlas

ModelMap is a source-grounded encyclopedia and knowledge graph for the history and evolution of large language models, with high-resolution coverage of 2023 onward and a compact foundation covering the Transformer era that precedes it.

The project is designed around a simple principle:

**sources → claims → entities + relationships → timelines, comparisons, narratives, and executable architecture references**

Rather than maintaining facts independently across prose pages, tables, and visualizations, ModelMap stores canonical structured records with provenance. Human-readable pages and graphs should be generated from that corpus.

## Scope

- **2017–2022:** compressed foundations — Transformer, pretraining, scaling, sparse computation, compute-optimal training, instruction tuning, and RLHF.
- **2023–present:** high-resolution history — model releases, architecture changes, training and post-training methods, inference systems, multimodality, reasoning, tool use, agents, datasets, benchmarks, and infrastructure.
- **Current year:** maintained as a versioned event stream rather than a finished historical chapter.

## What ModelMap distinguishes

A model family is not a release. A release is not a checkpoint. A checkpoint is not a product. A product is not an architecture.

The canonical ontology separates:

- model families, releases, and variants;
- architecture specifications and reusable techniques;
- pretraining and post-training runs;
- papers, repositories, model cards, and other sources;
- atomic claims and their evidence;
- datasets, benchmarks, evaluation protocols, and evaluation runs;
- organizations, historical events, licenses, hardware systems, and product systems;
- parameter lineage from conceptual architectural lineage.

## Evidence policy

Technically significant assertions should be traceable to evidence. The corpus uses explicit evidence states such as `confirmed_primary`, `reported_primary`, `independently_verified`, `inferred`, `disputed`, `superseded`, and `unknown`.

Unknown details remain unknown. ModelMap does not silently turn estimates, community lore, or architectural guesses into facts.

## Repository layout

```text
ModelMap/
├── data/                 # canonical records
├── docs/                 # ontology and editorial specifications
├── schemas/              # JSON Schema contracts
├── implementations/      # future executable architecture atlas
├── narratives/           # source-grounded historical synthesis
├── pipelines/            # future ingestion/validation/build tooling
├── tests/                # corpus and implementation validation
└── site/                 # future generated encyclopedia interface
```

## M0 — Canonical Ontology & Evidence Engine

The first milestone establishes the knowledge system before large-scale content ingestion:

- stable identifiers;
- entity ontology;
- claim/evidence representation;
- relationship vocabulary;
- source representation;
- architecture taxonomy;
- evaluation ontology;
- schema validation;
- provenance-preserving ingestion workflow.

See [`docs/ontology.md`](docs/ontology.md) and [`data/README.md`](data/README.md).

## Design principles

1. **Data first, prose second.** Timelines, comparison tables, graphs, and narratives derive from canonical records.
2. **Primary sources first.** Papers, technical reports, official repositories/configs, model cards, and release notes are preferred evidence.
3. **Claims are atomic.** A single claim should be independently supportable, disputable, and supersedable.
4. **Chronology and lineage are separate.** `what happened next` and `what idea descended from what` are different questions.
5. **Evaluation is protocol-aware.** Benchmark numbers are not treated as comparable without their evaluation settings.
6. **Readable implementations are labeled by fidelity.** Educational, reference, and verified implementations are distinct.
7. **Git is part of the historical record.** Changes to claims and evidence remain auditable.

## Status

ModelMap is at **foundation v0.1**. The repository is establishing its ontology and evidence contracts before ingesting the first canonical model families and techniques.
