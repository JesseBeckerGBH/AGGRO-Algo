# Vertical Slice — build record

Stage 2 of `implementation-order.md`: "Pick a single real mission you actually
care about and make it work end to end, ugly." Code lives in `src/research_os/`.

## Decisions taken (so the build could start)

| Choice | Decision | Why |
|---|---|---|
| Language | Python 3.11+ | `.gitignore` and `sqlite-schema.md` already assumed it |
| First connector | Brave Search API | free tier, real key in minutes; `connector-strategy.md` lists it |
| Runs with no key | `fixture` connector (canned corpus) | the pipeline is testable today; Brave slots in later |
| Mission | `missions/example-tennis-features.yaml` | copy it, edit the fields, point `--mission` at yours |

## What the slice does

1. **Query family** — `planning.plan()` reads `configs/query-families.yaml`,
   fills the angle templates from mission fields, forces the `disconfirming`
   and `adjacent_field` angles on medium/high novelty, refuses < 3 angles.
2. **Retrieve** — one connector, `raw_rank` preserved.
3. **Canonicalize + dedupe** — strip tracking params / `www` / trailing slash,
   sort query args, hash `title+snippet` and the snippet alone; drop exact
   duplicates (best origin rank wins).
4. **Classify** — exactly one source class per result, from operator
   allow/block lists → domain map → TLD pattern → `aggregator` default.
5. **Novelty** — `seen_before` (content hash or canonical URL already stored)
   and `novel_domain` (this mission has never stored that domain), from SQLite.
6. **Rerank** — **class bucket first**, then `relevance × class_weight ×
   penalty_mult × bonus_mult` within the bucket. A `primary` result never
   sorts below a `high_trust_secondary`, etc. Penalties (domain repetition,
   near-duplicate, already-seen, no-named-author) and the novel-domain bonus
   come from `source-classes.yaml`.
7. **Briefing** — `briefing.render()` emits the `briefing-agent.md` structure:
   bottom line, what is new (near-dupes and seen items excluded), what
   contradicts it (own section, explicit "none" when empty), confidence with
   the specific gap, next question, one-line footer.
8. **Persist** — `missions`, `queries`, `results`, `briefings` tables.

## Briefing synthesis — done, pending a key

`briefing.synthesize()` is implemented. `llm.py` is a provider-agnostic
`synthesize(system, user)` — `gemini` (default), `anthropic`, or `openai`,
each a stdlib REST call with no added dependency, picked by `LLM_PROVIDER`.
The prompt embeds the `briefing-agent.md` rules; the footer counts are
appended mechanically so they stay accurate whatever the model writes.
The HTTP call is injectable, so tests never hit the network.

`--brief render` (default) is unchanged and needs no key. `--brief llm` needs
one provider key in `.env`; `--brief auto` picks llm when a key is present.

## Success test — status

> The briefing tells you something you did not know, from a source you would
> not have found, in under 400 words.

**Ready to evaluate.** The pipeline produces a source-governed, deduped,
class-ranked, memory-aware result set (primary + named-expert ahead of
aggregators and forums; near-duplicate mirror and low-trust farm parked), and
`--brief llm` now turns that into the narrative. Outstanding: an API key, then
a real pass/fail judgement on a live mission.

## Next, in order

1. **Add a provider key** (`GEMINI_API_KEY` free tier is enough) and run
   `--brief llm` against the fixture, then judge the output.
2. **Run a live mission** with `--connector brave --brief llm`.
3. **Only then** Stage 3 (second connector, shared result schema) — measure
   whether multi-engine actually raises novelty yield or just volume.

Do not build the scheduler (Stage 5) against this until step 1 passes.
