# Seed corpus v0.1

The first ModelMap corpus is intentionally small. Its job is to exercise the ontology and provenance chain before broad ingestion.

It establishes three proof paths:

1. **attention lineage:** multi-head attention → multi-query attention → grouped-query attention;
2. **latent attention adoption:** DeepSeek-V2 and DeepSeek-V3 using multi-head latent attention;
3. **sparse-compute lineage:** sparse mixture-of-experts → DeepSeekMoE, followed by DeepSeek-V2/V3 adoption.

Every graph edge in this seed is backed by an atomic claim and a primary paper or technical report. The seed deliberately does **not** create a direct lineage edge from GQA to MLA: shared motivation or chronology is not sufficient evidence for ancestry.

Primary sources represented: arXiv:1911.02150, arXiv:2305.13245, arXiv:2401.06066, arXiv:2405.04434, and arXiv:2412.19437.
