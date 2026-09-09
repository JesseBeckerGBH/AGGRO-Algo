# src/ — Stage 2 vertical slice

One ugly end-to-end path, so the ranking logic finally produces an output you
can judge. See `docs/operations/implementation-order.md` (Stage 2) and
`docs/operations/vertical-slice.md`.

```
mission YAML
  -> planning.plan()        query family from configs/query-families.yaml
  -> connectors/            fixture (offline, default) | brave (needs API key)
  -> canonical.enrich/dedupe  canonicalize URLs, hash content, drop exact dupes
  -> classify.classify()   one source class per result (configs/source-classes.yaml)
  -> memory.mark_novelty()  seen-before / novel-domain from SQLite
  -> rerank.rerank()       CLASS BUCKET FIRST, then score within the bucket
  -> briefing.render()     structure from prompts/briefing-agent.md
  -> memory                missions / queries / results / briefings tables
```

## Run it

```bash
python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"      # Windows
# python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"       # POSIX

python -m research_os run --mission missions/example-tennis-features.yaml
pytest -q
```

No keys needed — the default `fixture` connector ships a canned corpus.
For live search: `cp .env.example .env`, add `BRAVE_SEARCH_API_KEY`, then
`--connector brave`.

## Deliberately stubbed (not this stage)

- **Briefing synthesis** — `briefing.render()` arranges and labels sources; it
  does not write the 250–400 word narrative. That is an LLM call
  (`briefing.synthesize()`, raises `NotImplementedError`) and is the next step.
- **Content-inspection classifier signals** — citation density, originality,
  ad density, correction history need fetched page bodies; the slice classifies
  from URL + snippet only.
- **Adaptation loop** (`configs/adaptation-rules.yaml`) — Stage 6–7.
- **Second/third connectors, scheduler** — Stage 3 / Stage 5. Do not build
  these until the success test passes.

## Layout

| Module | Responsibility |
|---|---|
| `models.py` | `Mission`, `Query`, `Result`, `Briefing` dataclasses |
| `config.py` | loads `configs/*.yaml`; `class_weight()`, `angle_set()` |
| `planning.py` | mission → query family (deterministic stand-in for the LLM planner) |
| `connectors/` | `fixture`, `brave`, `get_connector()` |
| `canonical.py` | URL canonicalization, hashing, exact-dupe removal |
| `classify.py` | source-class assignment |
| `rerank.py` | the governing rule: class before relevance |
| `memory.py` | SQLite persistence + novelty |
| `briefing.py` | render (deterministic) + `synthesize()` seam |
| `pipeline.py` | wires it together; `run_mission()` |
| `__main__.py` | `research-os run …` CLI |
