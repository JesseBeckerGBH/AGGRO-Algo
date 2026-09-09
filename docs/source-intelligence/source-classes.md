# Source Classes

## Objective

This document defines the source hierarchy for the Personal Research OS. The system’s most important rule is that every result should be scored first by source class before any other factor. This prevents the workflow from inheriting the biases of default platform ranking.[cite:11]

## Core hierarchy

### Tier 1 — Primary Sources

These are original materials closest to the underlying reality being studied.

Examples:
- Official documentation.
- Regulatory filings.
- Original datasets.
- Direct company statements.
- Original research publications.
- Transcripts, speeches, public records, and first-party releases.

Default treatment:
- Highest priority.
- Strong authority assumption, subject to authenticity checks.

### Tier 2 — High-Trust Secondary Analysis

These sources interpret primary materials well and add real synthesis.

Examples:
- Respected specialist journalism.
- Deep technical analysis.
- Reputable research newsletters.
- Domain-specific publications with known editorial quality.

Default treatment:
- High priority.
- Preferred when primary sources are too raw or fragmented.

### Tier 3 — Credible Practitioners and Named Experts

These sources reflect experienced operators, researchers, or domain specialists with track records.

Examples:
- Recognized technical experts.
- Credible founders or operators writing in their field.
- Specialist analysts with demonstrated domain competence.

Default treatment:
- Medium-high priority.
- Use to augment primary and secondary sources, not replace them.

### Tier 4 — Aggregators and Summaries

These collect and summarize information but rarely originate it.

Examples:
- News aggregators.
- General summaries.
- Curated collections.

Default treatment:
- Useful for discovery.
- Rarely top-ranked in final outputs.

### Tier 5 — Forums and Social Signals

These are exploratory environments that may surface novelty but often contain noise.

Examples:
- Forums.
- Social media posts.
- Community discussion threads.
- Comment-driven pages.

Default treatment:
- Useful for weak-signal discovery only.
- Never allowed to dominate final ranking by default.

### Tier 6 — Low-Trust or SEO-Heavy Sources

These sources often optimize for traffic capture rather than information value.

Examples:
- Generic AI-generated content farms.
- Thin affiliate pages.
- Low-substance rewrites.
- Summary pages with little original insight.

Default treatment:
- Deprioritized or blocked.

## Scoring policy

Results are ranked in this order:
1. Source class.
2. Mission relevance.
3. Novelty versus memory.
4. Recency when relevant.
5. Authority signals.
6. Redundancy penalties.

This reflects the earlier guidance that source-class-first ranking is the alignment rule that keeps the entire system stable.[cite:11]

## Dynamic upgrades and downgrades

A source can move between practical trust tiers over time. A supposedly strong domain can decline in value, and a lesser-known source can prove consistently useful.

Upgrade conditions:
- Repeatedly produces novel, high-signal, accurate outputs.
- Frequently points toward high-value primary material.
- Performs well in operator usefulness reviews.

Downgrade conditions:
- Increasing redundancy.
- Thin summaries.
- SEO-style repetition.
- Low briefing utility.
- Pattern of citation chains leading only to weaker summaries.

## Self-annealing layer

The source-class system should learn from outcomes. If a source repeatedly appears in low-value briefings, triggers operator rejection, or contributes to duplication rather than novelty, the system should reduce its weight automatically and log the adjustment.

Conversely, if a domain repeatedly delivers high-value discoveries or strong briefable insights, it should receive an adaptive boost. This is how the product becomes more resilient and less dependent on static trust assumptions.
