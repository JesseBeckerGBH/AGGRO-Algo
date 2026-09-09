# Scheduler Plan

## Objective

The scheduler exists to run high-value research missions automatically and produce compact outputs without forcing the operator to manually trigger every cycle. The earlier workflow identified the scheduler and daily briefing layer as the next major build step after the core pipeline was in place.[cite:10]

## Scheduler roles

The scheduler should manage three categories of work:

### 1. Routine monitoring

Recurring missions that watch known domains, topics, competitors, technologies, or market shifts.

### 2. Active investigations

Higher-priority missions with more aggressive collection, broader query families, and tighter review windows.

### 3. System maintenance

Dedup checks, source drift checks, connector health checks, profile hygiene reminders, and adaptation review cycles.

## Scheduling strategy

- Daily runs for core monitoring.
- Event-driven runs for urgent topics.
- Weekly maintenance runs for drift and failure audits.
- Monthly recalibration runs for source and scoring review.

## Briefing output rules

Each run should aim to produce one compact, high-signal output rather than a full raw dump. This reflects the earlier design goal of delivering short founder or operator briefs instead of overwhelming link piles.[cite:10]

A standard briefing should include:
- What changed.
- Why it matters.
- Which sources matter most.
- What is genuinely new.
- What action, if any, is recommended.

## Failure handling

The scheduler must not treat all failure as equal.

- Missed run: retry according to policy.
- Connector outage: fail over and log.
- Low-value run: reduce mission priority or modify query plan.
- Redundancy spike: force broader source exploration.
- Briefing irrelevance: trigger ranking review.

## Self-annealing layer

A self-annealing scheduler should adapt frequency, breadth, and retry logic according to outcome quality.

Examples:
- If a mission keeps producing stale results, reduce frequency or alter query families.
- If a mission repeatedly produces valuable new material, increase its cadence.
- If connector outages cluster, route around them.
- If drift alerts rise, schedule a recalibration run automatically.

## Product implication

For a subscription product, the scheduler is part of the service value. Customers are paying for recurring judgment-ready outputs, not a manual search console.[cite:14]
