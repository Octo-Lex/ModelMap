# 2023 — High-resolution chapter

This directory is the editorial layer for ModelMap's first high-resolution historical year. Canonical dates, releases, organizations, and technical assertions live under `data/`; this narrative layer should explain their significance without becoming a second fact store.

Generate the current chronology with:

```bash
python tools/build_year.py 2023 --format markdown
```

## Editorial themes

The eventual chapter should explain 2023 through multiple concurrent trajectories rather than a single model leaderboard:

- frontier scale and multimodality;
- the expansion of open-weight model ecosystems;
- inference-efficient attention and smaller high-performing models;
- synthetic and curated training-data strategies;
- post-training, tool use, and planning capabilities;
- native multimodality as a model-family design direction;
- the accelerating separation between model releases, research reports, APIs, and user-facing products.

## Editorial rule

Every factual statement introduced here should resolve to canonical ModelMap claims/events or add the missing claim with evidence first. Unknown architecture details for closed models must remain unknown.
