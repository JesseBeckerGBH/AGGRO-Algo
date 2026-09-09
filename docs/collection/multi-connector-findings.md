# Stage 3 — multi-connector findings

Second connector added: **Marginalia** (`src/research_os/connectors/marginalia.py`) —
an independent engine that indexes the small, non-commercial, text-first web.
Chosen precisely because its domain distribution barely overlaps a mainstream
engine's, which is the hard test of the novelty claim.

Run: `--connector brave,marginalia` on `example-tennis-features`.

## What the data says

| | Brave only | Brave + Marginalia |
|---|---|---|
| Results retrieved | 73–80 | 133–140 (marginalia ~60) |
| Distinct domains in the **pool** | ~40 | **~80** |
| Distinct domains **in the briefing** | 2–3 | **3** |
| New strong-class source surfaced | — | `dash.harvard.edu`, `pmc.ncbi.nlm.nih.gov` (both classified primary) |
| New *idea* surfaced | — | intransitive-dominance graph embeddings (GNN) feature |

The implementation order asks: *does multi-engine collection raise novelty
yield, or merely raise volume?*

**Answer: mostly volume, with occasional real value.** The pool roughly
doubled in domain diversity, but the briefing stayed concentrated on three
high-class domains. That is the reranker working as designed — Marginalia's
long-tail pages are mostly `aggregator` / `community` / `low_trust` class and
are correctly kept below the arXiv primaries. The second connector pays off
only when the long-tail happens to contain a strong-class source Brave missed
— which it did twice here (a Harvard win-probability paper, a PubMed Central
paper) plus one genuinely new feature idea.

## Implication

Marginalia is **not a general novelty engine for academic missions** — for
"which arXiv features predict X", Brave already reaches the good sources. Its
value would be higher for missions where the good sources *are* on the indie
web: practitioner write-ups, niche primary documents, forum-sourced failure
modes. Keep it, but expect its contribution to be mission-dependent, and let
the adaptation loop (Stage 7) down-route it per mission class when it only
adds volume.

## Bugs found and fixed in this stage

1. **Near-duplicate papers slipped through** — "Statistical enhance learning…"
   and "Statistical enhanced learning…" (same paper, two landing pages).
   `rerank._title_words` now stems (`-s/-ed/-ing`) and strips "… / GitHub"
   noise; near-dup fires at Jaccard ≥ 0.55 *or* ≥ 5 shared stem-words on the
   same domain.
2. **"What contradicts it" was always empty** — disconfirming-angle results
   were being outranked out of the top cut. `briefing` now pulls
   disconfirming-angle hits from the *full* ranked set for that section (both
   `render` and `synthesize`), and `planning` uses a cleaner disconfirming
   query (`<subject> prediction limitations OR overfitting OR …`). The Stage 3
   LLM run now returns three concrete caveats (linear models miss feature
   interactions; point-level class imbalance on returner-victory states;
   overfitting without regularisation).

## Next

- Strengthen the disconfirming angle further and add a `quantitative` angle to
  the high-novelty set.
- Consider a third connector only for a mission whose good sources are
  non-academic — otherwise it is volume.
- Stage 4 (memory / novelty scoring) and Stage 6 (telemetry) before Stage 7.
- Still no scheduler (Stage 5).
