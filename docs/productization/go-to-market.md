# Go-to-market — decision record

Supersedes the "high-agency knowledge workers" broad framing in
`archives/original-drop/algorithm-changer-how-to-explain.txt`. That file's
segment table already flagged competitive intelligence as a strong enterprise
fit; a second, independent GTM analysis (ChatGPT, pasted into chat 2026-09-10)
converged on the same buyer from a different angle. Two independent reads
landing on the same lane is the signal this decision is built on.

## ICP (adopted)

**Product-marketing and competitive-intelligence teams at B2B companies.**
Not "professionals" broadly. They research competitors, pricing, launches,
regulation, and market shifts *repeatedly*, they are reachable through named
communities, and they can buy without bank/law-firm-grade procurement.

Their job description is the mission-planner/briefing loop this system
already runs. They do not need to be sold the concept.

## Where to reach them

| Channel | Notes |
|---|---|
| Product Marketing Alliance + its Slack (50k+ members) | participate via useful research/workshops, not pitching |
| SCIP (scip.org) | most concentrated audience — CI is the literal job title |
| Competitive Intelligence Alliance | adjacent, smaller |
| LinkedIn / targeted outreach | titles: Head/Director of Competitive Intelligence, Director of Product Marketing, Market Intelligence Manager, VP Strategy, Chief of Staff, Corporate Development Director |
| Chief of Staff Network (900+) | good second segment — same "messy inputs to decisions" job |
| Pavilion (10k+) | later — partnership/webinar channel once there is customer evidence |

## Positioning

> Know what actually changed, why it matters, where the evidence came from,
> and what credible sources disagree about — without rereading the same story
> twenty times.

Never "AI news feed," "search engine," or "better summary tool" — those
categories already sound like the problem.

## Why this isn't "AlphaSense with extra steps"

AlphaSense and Feedly Market Intelligence already sell trusted aggregation +
AI synthesis + citations to this exact buyer. That validates the budget line
exists. It also means "everything in one place with AI summaries" is not
differentiation anymore — it's the entry ticket.

The product's actual mechanics back a sharper claim than "more AI." Check the
pitch against what is already built, not aspirational:

| Claim | Where it's real |
|---|---|
| source provenance on every claim | every briefing line carries `(domain, class)` — `briefing.py` |
| duplicate/recycled suppression | canonical dedup + near-duplicate detection — `canonical.py`, `rerank.py` |
| conflicting-source detection | "What contradicts it" is a mandatory section, never silently omitted — `briefing-agent.md` |
| novelty relative to what's known | `novelty_score` / novelty yield, memory-backed — `novelty.py` |
| user priorities, not engagement optimization | `no_engagement_optimization` is a hard invariant in `adaptation-rules.yaml`, not a talking point |
| governed, not a black box | the ranking rule (class before relevance) is a config file the buyer can read |
| gets better at THEIR landscape over time, bounded and reversible | the Stage 7 self-annealing loop — live-proven, not theoretical |

Lead with the last two in CI-specific outreach — an auditable policy and a
system that logs and reverses its own mistakes is a claim AlphaSense cannot
make about itself, and "auditable" lands specifically with a
compliance-adjacent buyer.

## Whop — deferred, not needed yet

Whop is built for consumer/creator subscriptions with self-serve checkout.
Wrong tool for 10-20 hand-picked B2B design partners. For the launch motion
below, use a Stripe payment link (or an invoice) for money and Slack Connect
or email for delivery. Revisit Whop only if/when there is a cheaper self-serve
tier for individual analysts — a different, later product decision.

## Launch motion (Stage 9, from implementation-order.md — independently
## re-derived by both GTM analyses)

1. 10-20 design partners in **one** profession (CI/PMM).
2. Produce their brief manually or semi-manually for several weeks before
   selling the repeatable workflow.
3. Measure, per partner:
   - research hours eliminated
   - redundant items suppressed
   - developments caught earlier than their normal process
   - % of claims the partner actually verified (trust signal)
   - decisions / presentations / client deliverables the brief informed
4. Price against decisions improved, not links delivered, once evidence exists
   (`service-offer.md` tier ladder already reflects this).

## Immediate action items

1. Pick 3-5 real target companies/topics in a CI person's actual world (a
   competitor, a pricing move, a regulatory shift in one industry).
2. Run real missions on them with the CLI today — no new code needed.
3. Hand-deliver the sample briefing itself as the outreach artifact — not a
   demo. See `docs/productization/outreach-templates.md`.
4. Share the one-pager (published as an Artifact — ask for the current link)
   when a prospect wants something to forward internally.

## What NOT to do

- No fabricated logos, testimonials, or usage stats before there are real
  ones. "Design partner" / "early access" framing is honest at this stage and
  this audience responds well to it — analysts like shaping the product.
- No broad consumer marketing yet — low willingness to pay, and credibility
  battles this business doesn't need before it has one identifiable job market
  proven out.
