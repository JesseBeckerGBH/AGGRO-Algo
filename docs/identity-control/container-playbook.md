# Container Playbook

## Objective

This playbook defines how to separate online identities and browsing contexts so that search, discovery, and research work are not continuously contaminated by one persistent profile. Identity control is one of the primary mechanisms for escaping dysfunctional algorithmic loops.[cite:11]

## Principles

- One identity trail should not control every search context.
- Research should happen in cleaner environments than entertainment or logged-in personal browsing.
- Experimental and noisy behavior should be isolated by design.
- Containers are not a cosmetic convenience; they are part of the ranking-defense architecture.[cite:11]

## Recommended profile structure

### 1. Clean Research

Use for deliberate research missions, evidence gathering, and source evaluation.

Rules:
- Minimal extensions.
- Minimal login state.
- No casual entertainment use.
- No social feeds during research sessions.
- Search queries logged to mission records.

### 2. Work Logged-In

Use for necessary account-based work that still requires platform access.

Rules:
- Restricted to business tooling, email, documentation, and verified services.
- Do not mix broad exploratory search here unless necessary.

### 3. Personal Logged-In

Use for ordinary life, commerce, social use, and personal communication.

Rules:
- Assume this context is heavily personalized.
- Never treat it as a clean research environment.

### 4. Experimental/Noise Injection

Use for intentional divergence, query experiments, contrast testing, and source discovery.

Rules:
- Can be messier by design.
- Must never contaminate Clean Research.
- Good for testing how different identities shape result sets.

### 5. Publishing/Observation

Use for checking how external platforms surface your own content, product pages, or future customer-facing assets.

Rules:
- Observe discoverability and ranking behavior without merging this identity into research memory.

## Setup guidance

A practical implementation can use browser profiles, Firefox containers, separate browser instances, or VM-separated sessions. The exact tool matters less than disciplined separation. The original design intent was to use containers to keep research identities from being shaped by unrelated browsing behavior.[cite:11]

## Hygiene rules

- Do not stay signed into everything everywhere.
- Do not use one tab set for all purposes.
- Close context-specific sessions when work ends.
- Keep bookmarks separate by context.
- Review extension sprawl monthly.
- Track which profile produced which result set.

## Operational workflow

1. Start in Clean Research for planned missions.
2. If a query family starts collapsing into familiar results, test contrast in Experimental/Noise Injection.
3. If account access is needed, move temporarily into Work Logged-In, then return to Clean Research.
4. Log identity context in mission metadata.

## Self-annealing additions

Identity drift should be monitored. If the Clean Research profile starts showing the same contamination symptoms as broader personal browsing, the system should flag the profile for reset, extension audit, cookie purge, or replacement.

Suggested self-annealing triggers:
- Same domains dominating unrelated missions.
- Falling novelty yield from the clean profile.
- Persistent ranking distortion after query diversification.
- Increase in low-trust source presence.

## Deliverable for productization

For customer use, this playbook can become:
- An onboarding checklist.
- A guided setup wizard.
- A managed “algorithm reset” service component.
- A premium support offer for research-environment hardening.[cite:14]
