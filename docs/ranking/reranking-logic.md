# Reranking Logic

## Objective

Reranking is the decisive layer where external ranking gives way to internal judgment. Without reranking, the system is only aggregating platform outputs. With reranking, it becomes an intentional research operating system.[cite:10][cite:11]

## Ranking order

The recovered logic is:
1. Source class.
2. Relevance to mission.
3. Novelty versus stored memory.
4. Recency when appropriate.
5. Authority refinement.
6. Redundancy penalties.[cite:11][cite:10]

## Scoring dimensions

### Source class score

Highest-weight feature. Determines the trust and priority band before other factors are considered.[cite:11]

### Mission relevance score

Measures semantic and practical fit to the mission objective.

### Novelty score

Measures whether the item adds new insight, new evidence, new domain exposure, or a genuinely distinct angle relative to existing memory.[cite:10]

### Recency score

Used selectively. Some missions require freshness, while others value canonical depth over timing.

### Authority refinement

Adjusts scoring based on domain reputation, author quality, source consistency, and prior usefulness history.

### Redundancy penalty

Suppresses near-duplicates, mirrored summaries, repeated domains, and thin rewrites.[cite:10]

## Hard filters

Items may be blocked or heavily penalized if they show:
- Thin content patterns.
- Low-trust aggregation.
- SEO capture behavior.
- Repeated low-value usefulness ratings.
- Excessive duplication.

## Operator override

The operator should be able to mark results as:
- Promote.
- Neutral.
- Suppress.
- Never show again.

These overrides should feed future adaptive behavior instead of remaining one-off actions.

## Self-annealing layer

Self-annealing reranking means the system records where its ranking failed and changes future scoring accordingly.

Failure classes include:
- High-ranked result proved unhelpful.
- Low-ranked result should have been surfaced.
- Too many results from one domain.
- Novelty score overestimated weak results.
- Recency overweighted shallow content.

Adaptive responses include:
- Weight updates.
- Domain caps.
- Source-class correction.
- Query-specific scoring adjustments.
- Future suppression or promotion rules.

## Design rule

Automation should scale discernment, not volume. If reranking starts surfacing more material but less value, the system is drifting and must self-correct.[cite:10][cite:11]
