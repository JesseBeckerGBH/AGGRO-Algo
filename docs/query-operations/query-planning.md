# Query Planning

## Objective

Query planning exists to stop repetitive, vague, or habit-driven search behavior from determining what the system sees. The workflow begins with query planning because bad search loops often begin with repeated query structures long before ranking happens.[cite:10]

## Mission-first approach

Every search session should begin with a mission, not a vague curiosity. A mission states:

- What is being investigated.
- Why it matters.
- Which source classes are preferred.
- Whether novelty or confirmation is the main need.
- Whether recency matters.
- What a useful answer would look like.

## Query template

Each mission should generate a small family of query types:

1. Direct factual query.
2. Primary-source query.
3. Contrarian query.
4. Freshness-oriented query.
5. Terminology-variant query.
6. Expert or named-source query when available.

The purpose is not to spray random queries. It is to prevent one phrasing from collapsing the entire result space into one algorithmically familiar corridor.

## Mission sheet format

For each mission, capture:

- Mission ID.
- Goal.
- Key terms.
- Excluded terms.
- Priority source classes.
- Query family.
- Review deadline.
- Success condition.
- Failure indicators.

## Examples of good planning behavior

- Break one broad question into several narrower evidence-seeking queries.
- Ask for original materials before summaries.
- Test whether different language surfaces different source classes.
- Preserve query intent so later reranking can judge relevance correctly.

## Failure patterns to avoid

- Repeating the same broad phrase every day.
- Starting with summary-seeking instead of evidence-seeking.
- Over-trusting autocomplete and suggested queries.
- Mixing exploration, validation, and monitoring into one search string.

## Self-annealing layer

The planner should learn which query families produce strong outcomes. Over time, the system should detect low-yield patterns, stale term clusters, and repeated phrase structures that no longer open new territory.

Adaptive behaviors should include:
- Penalizing low-yield query templates.
- Promoting query variants that surface better source classes.
- Rotating terminology when novelty drops.
- Recommending contrarian or orthogonal formulations when result diversity collapses.

## Product implication

For subscription delivery, this document can become the hidden planning engine behind customer briefings. End users may never see the full query architecture, but the product’s differentiation will depend heavily on it.[cite:14]
