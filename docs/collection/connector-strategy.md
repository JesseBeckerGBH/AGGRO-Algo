# Connector Strategy

## Objective

This document defines how the system collects search results and related web inputs without becoming dependent on a single ranking environment. The recovered workflow used a multi-engine collector so outside personalization would have less unilateral control over what enters the pipeline.[cite:10][cite:11]

## Supported connector classes

The original workflow identified these collection paths:
- Kagi.
- Brave Search.
- Self-hosted or local SearXNG.
- Constrained DuckDuckGo HTML fallback.[cite:10]

These connectors should be treated as acquisition channels, not truth engines.

## Collection rules

- Prefer approved APIs where available.
- Use low concurrency.
- Respect rate limits.
- Preserve request and result logs.
- Normalize outputs into a common schema.
- Keep connector behavior deterministic and reviewable.[cite:10]

## Normalized result schema

Each collected result should include:
- Connector name.
- Query ID.
- Timestamp.
- Raw title.
- URL.
- Canonical URL if resolved.
- Snippet.
- Domain.
- Rank position.
- Source-class guess.
- Retrieval notes.

## Connector roles

### Precision connectors

Use when looking for stronger quality and better relevance under intentional queries.

### Breadth connectors

Use when trying to break out of a result rut and explore broader source neighborhoods.

### Fallback connectors

Use when the preferred connectors fail, throttle, or produce blind spots.

## Health checks

Connector health should be monitored continuously:
- Availability.
- Latency.
- Error rate.
- Duplicate rate.
- Source-class distribution.
- Drift from expected quality bands.

## Self-annealing layer

A self-annealing connector strategy does not just retry after failure. It diagnoses whether the failure was operational or epistemic.

Examples:
- If a connector is down, fail over to a backup.
- If a connector returns repetitive low-value domains, reduce its weighting for certain mission classes.
- If one connector is consistently best for a query family, increase its routing share there.
- If connector disagreement is high, trigger a wider comparison run instead of trusting a single path.

## Product implication

In a customer-facing system, connector orchestration becomes part of the moat. The user pays not merely for “web search,” but for intelligent routing, cleaner aggregation, and more resilient collection behavior.[cite:14]
