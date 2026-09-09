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
python -m research_os run --mission missions/example-tennis-features.yaml --brief auto
pytest -q
```

No keys needed for the default run — the `fixture` connector ships a canned
corpus and `--brief render` is deterministic. To go live: `cp .env.example .env`,
then add `BRAVE_SEARCH_API_KEY` (`--connector brave`) and/or an LLM key
(`--brief llm`). `--brief auto` uses the LLM if a key is present, else render.

## Briefing modes

| `--brief` | Behaviour |
|---|---|
| `render` (default) | Deterministic: arranges + labels sources into the briefing-agent.md structure. No key. |
| `llm` | LLM writes the 250–400 word narrative over the reranked set, obeying briefing-agent.md. Needs a key; footer counts still appended mechanically. |
| `auto` | `llm` if any provider key is configured, else `render`. |

Providers (`llm.py`, picked by `LLM_PROVIDER`, default `gemini`): `gemini`,
`anthropic`, `openai` — each a stdlib REST call, no extra dependency.

## Deliberately stubbed (not this stage)

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
| `briefing.py` | `render()` (deterministic) + `synthesize()` (LLM) |
| `llm.py` | provider-agnostic `synthesize()` — gemini / anthropic / openai |
| `env.py` | `.env` loader (no dependency) |
| `pipeline.py` | wires it together; `run_mission()` |
| `__main__.py` | `research-os run …` CLI |
