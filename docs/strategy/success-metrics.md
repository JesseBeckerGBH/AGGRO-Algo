# Success Metrics

## Purpose

This document defines how to tell whether the Personal Research OS is actually helping a person escape an algorithmic rut instead of merely generating more output. The system should be evaluated on signal quality, novelty, decision usefulness, recovery behavior, and long-term adaptability.[cite:10][cite:11]

## Primary metrics

### 1. Source Quality Score

Measure the percentage of surfaced results that come from preferred source classes. The core rule remains source-class-first ranking, so the system should continuously increase the share of primary sources, high-trust secondary analysis, and credible domain experts in the top results.[cite:11]

Target:
- 70 percent or more of top-10 results drawn from approved high-trust source classes.
- Less than 10 percent of top-10 results from deprioritized SEO-heavy or low-substance classes.

### 2. Novelty Yield

Measure how many surfaced items are materially new relative to stored memory. Novelty should be defined by domain, author, document type, claim pattern, and insight contribution rather than URL uniqueness alone.[cite:10]

Target:
- At least 20 to 30 percent of briefing items should be genuinely new at the beginning of deployment.
- Later, novelty can decline moderately if quality remains high, but repeated low-value duplication should be actively penalized.

### 3. Redundancy Suppression

Measure how often near-duplicate, mirrored, or summary-only results are filtered out before final presentation. A high-functioning system should suppress false variety aggressively.[cite:10]

Target:
- 80 percent or more of obvious duplicates removed before briefing generation.

### 4. Decision Utility

Measure whether the final briefings help the operator make decisions. This can be scored by a simple operator review after each briefing: useful, partially useful, or not useful.

Target:
- 70 percent or more of daily briefings rated useful.
- Less than 10 percent rated not useful.

### 5. Time-to-Signal

Measure time spent from mission start to usable insight. The system exists to reduce cognitive drag, not increase it.[cite:10]

Target:
- Daily briefing ready within a bounded operational window.
- Operator review time under 10 minutes for routine briefings.

## Self-annealing metrics

### 6. Error Capture Rate

Measure how often the system records its own failures: missed sources, bad rankings, noisy domains, stale missions, broken connectors, low-value summaries, or briefing irrelevance.

Target:
- Every operational failure generates a structured event in the error log.
- Zero silent failures in production-grade workflows.

### 7. Recovery Success Rate

Measure whether the system improves after a detected failure. A self-annealing system should not only log mistakes but change future behavior in response.

Target:
- At least 60 percent of repeated failure types should show measurable reduction after mitigation rules are applied.

### 8. Drift Detection Sensitivity

Measure the ability to detect when novelty falls, source quality slips, or one domain begins dominating output.

Target:
- Drift alerts triggered before quality collapses into a visible rut.

## Business metrics

### 9. Product Repeatability

Measure how well the workflow can be reused across users, verticals, or industries. This matters because the long-term goal is productization and subscription delivery.[cite:14]

Target:
- Core setup reproduced with minimal customization across at least three user archetypes.

### 10. Retention Value

Measure whether recurring briefings remain worth paying for.

Target:
- Users continue to open and rate briefings positively over a sustained period.
- Operators perceive lower search fatigue and higher confidence in discovery quality.

## Review cadence

- Daily: briefing utility, connector health, obvious ranking mistakes.
- Weekly: source quality, novelty yield, redundancy suppression.
- Monthly: drift patterns, failure classes, monetization readiness, packaging quality.

## Decision rule

If volume rises while usefulness, novelty, and source quality fall, the system is regressing. If source quality, novelty-adjusted usefulness, and recovery behavior improve together, the system is succeeding.[cite:10][cite:11]
