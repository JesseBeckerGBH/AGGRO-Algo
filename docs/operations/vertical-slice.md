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

## Success test — status

> The briefing tells you something you did not know, from a source you would
> not have found, in under 400 words.

**Partially met.** The slice reliably produces a source-governed, deduped,
class-ranked, memory-aware briefing that surfaces primary and named-expert
material ahead of aggregators and forums, and correctly parks a near-duplicate
mirror and a low-trust content farm. It does **not** yet synthesise a novel
insight in prose — `render()` arranges and labels; it does not write the
narrative. That is `briefing.synthesize()` (an LLM call, currently
`NotImplementedError`) and is the immediate next step.

## Next, in order

1. **`briefing.synthesize()`** — LLM narrative over the reranked set, still
   obeying `briefing-agent.md` (class label on every claim, lead with what
   changed, refuse to manufacture significance). Then the success test is a
   real pass/fail.
2. **Run it against a live mission** with `--connector brave` and a key.
3. **Only then** Stage 3 (second connector, shared result schema) — measure
   whether multi-engine actually raises novelty yield or just volume.

Do not build the scheduler (Stage 5) against this until step 1 passes.
