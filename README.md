# Personal Intelligence Infrastructure

A self-annealing research and learning operating system for source-governed discovery, durable knowledge, and adaptive answer paths.

## Product Thesis

The system does not claim to rewrite external search algorithms or make users intrinsically smarter.

It provides an expert-grade research environment: mission-first query design, multi-source retrieval, source-class-first reranking, persistent memory, learning-aware feedback, and controlled self-annealing.

Two people can type the same words into a search box and get very different outcomes — not because one is smarter, but because one brings better source judgment, better vocabulary, accumulated memory of what has already been ruled out, and the ability to ask a stronger follow-up question. This system productizes that advantage.

## Positioning

> It helps the internet respond to you better, and it helps you become better at using the internet.

**Category:** Personal Intelligence OS — user-owned cognitive infrastructure that sits between a person and the internet, replacing passive algorithmic discovery with intentional research, memory, source judgment, learning feedback, and adaptive improvement.

**Technical definition:** a self-annealing, source-governed research and learning operating system.

## Core Capabilities

- Intentional research identities and context control
- Mission-based query planning
- Multi-engine retrieval
- Source-class-first ranking
- Deduplication and novelty detection
- Persistent research and learning memory
- Retrieval, synthesis, and transfer prompts
- Adaptive error correction with logged, reversible policy changes
- Compact decision and learning briefings

## Repository Structure

| Path | Purpose |
|---|---|
| `docs/` | Product philosophy, specifications, reports, workflow documentation |
| `skills/` | Reusable agent skill definitions — the behavioral constitution |
| `configs/` | Source, query, scoring, and adaptation policies (machine-readable judgment) |
| `prompts/` | Agent prompts and role instructions |
| `src/` | Application modules |
| `archives/` | Conversation exports, PDF copies, permanent source records |

## The Governing Rule

Every retrieved result is scored **by source class first**, before relevance, recency, or popularity. This single rule is what keeps the system from drifting back into the noise trap it was built to escape. If a change to the system would violate it, the change is wrong.

## Build Order

Judgment first, automation second, commercialization third. See `docs/operations/implementation-order.md`.

## Status

Stage 2 (vertical slice) building. The judgment layer (`configs/`) is written;
`src/research_os/` runs one mission end to end — query family, retrieval,
canonicalize + dedupe, source-class-first rerank, SQLite memory, briefing.
Runs offline with no API key. See `docs/operations/vertical-slice.md`.

```bash
python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"
python -m research_os run --mission missions/example-tennis-features.yaml
```

Not yet: LLM briefing synthesis, live-search validation, multi-connector,
scheduler, adaptation loop.
