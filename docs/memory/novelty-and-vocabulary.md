# Stage 4 — memory, novelty, and vocabulary escalation

"Novelty scoring is meaningless before memory exists." Stage 2 already stored
results and flagged `seen_before` / `novel_domain`. Stage 4 turns those into
graded signals and adds the two feedback loops the design calls for.

## 1. Per-mission domain concentration

New table `mission_domains(mission_id, domain, hits, first_seen, last_seen)`.
Every run increments hit counts; `Memory.domain_shares()` returns the per-domain
share and the top share. Watched against `adaptation-rules.yaml`
`domain_concentration_ceiling: 0.35`.

On the example mission the top domain sits at ~12% across 44 pool domains —
healthy spread, nowhere near the ceiling. `mark_novelty` now also fills
`Result.domain_prior_hits` so the reranker knows how hard this mission has
already leaned on a domain.

## 2. Graded novelty + novelty yield

`novelty.py`: `novelty_score in [0,1]` per result —

    +0.45  domain never seen for this mission
    +0.30  content / URL never seen before
    +0.25 * (1 - this domain's share of mission memory)

The score feeds the reranker as a **within-bucket** factor
(`0.85 + 0.30 * novelty_score`, i.e. 0.85x–1.15x) — it orders results inside a
class, it never lifts one class above another.

`novelty.yield_of(surfaced)` = share scoring ≥ 0.40. This is the number drift
detection watches against `novelty_yield_floor: 0.20`. The CLI prints it and
flags `[below 20% floor]`. Observed behaviour: run 1 on a fresh mission = 100%;
run 2 with warm memory = 0% and flagged — the intended "this run found nothing
new" signal for a recurring mission.

## 3. Promoted-vocabulary store

New table `promoted_vocab(mission_id, term, distinct_sources, status,
first_seen, decided_at)`, `status in {candidate, promoted, rejected}`.

`Memory.harvest_vocab()` mines **bigrams from the titles of primary-class
results** (title text only — snippet prose floods the harvest with glue like
"they extracted"), drops function words and generic ML phrases, and records any
bigram appearing across `>= 2` distinct primary **sources** as a `candidate`.
Capped at 10 new candidates per run. On the example mission a run yields ~3
candidates (e.g. `grand slam` from 3 sources) — low enough to review by hand.

Terms are **never auto-promoted** (`query-families.yaml`:
`operator_confirms_before_promotion`). The operator reviews and decides:

    research-os vocab --mission M.yaml                       # list
    research-os vocab --mission M.yaml --promote "grand slam" --reject "statistical enhanced"

`promoted` terms are folded into `mission.vocabulary_seed` at the top of the
next run, before query planning — verified end to end: a promoted term appears
in the regenerated query family.

## Known tuning targets (not blockers)

- Vocab harvest is bigram-frequency with a stoplist; precision is ~2/3 useful.
  The operator gate is the safety net. A later pass could restrict to the
  `primary_source_hunt` angle or add lightweight POS filtering.
- `novelty_score` weights are hand-set; they belong under the adaptation loop
  (Stage 7), not hand-edited mid-mission.

## Next

Stage 6 (structured failure logs + weekly drift check) reads the metrics this
stage produces — `mission_domains` concentration and `briefings.novelty_yield`
— against the thresholds in `adaptation-rules.yaml`. Stage 5 (scheduler) still
waits.
