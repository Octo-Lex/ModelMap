# 2024 — Architectural diversification and the reasoning transition

This directory is the editorial layer for ModelMap's 2024 high-resolution history. Dates and technical facts remain canonical under `data/`; narrative text should explain those records rather than duplicate them.

Generate the current year chronology with:

```bash
python tools/build_year.py 2024 --format markdown
```

## Editorial themes

The chapter should connect parallel developments rather than reduce the year to a leaderboard:

- long-context escalation, especially Gemini 1.5;
- multimodality becoming a first-class model design axis;
- continued expansion of open-weight ecosystems through Llama, Gemma, Qwen, Mistral, and DeepSeek;
- sparse conditional compute through MoE designs;
- architecture-level inference efficiency through GQA, MLA, local/global attention, and related mechanisms;
- richer supervision through distillation and multi-token prediction;
- the transition from conventional post-training toward reasoning-oriented reinforcement learning;
- explicit test-time compute scaling with the o1 series;
- the beginning of a model-to-agent/system transition visible in tool-oriented and agentic releases.

## Editorial rule

Every factual statement introduced here should resolve to canonical claims/events or add the missing evidence-backed record first. Closed-model internals remain unknown unless explicitly disclosed by a primary source.
