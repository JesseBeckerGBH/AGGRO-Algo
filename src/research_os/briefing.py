"""Render a reranked result set into a decision-support briefing.

Follows the structure in prompts/briefing-agent.md: bottom line, what is new,
what contradicts it (always its own section), confidence with the specific
gap, next question, one-line footer. Every claim carries its source class.

This is a DETERMINISTIC render — it arranges and labels, it does not
synthesise prose. Real synthesis (the 250-400 word narrative the success
test wants) is an LLM call and is the next step after the slice; the seam
is `synthesize()` below.
"""

from __future__ import annotations

from . import llm
from .models import Briefing, Mission, Result

_STRONG_CLASSES = {"primary", "high_trust_secondary", "named_expert"}
_CONTRA_CUES = (
    "criticism", "overstated", "does not", "doesn't", "fails", "myth",
    "debunk", "no evidence", "overfit", "spurious",
)


def _is_contradicting(r: Result) -> bool:
    if r.query_angle == "disconfirming":
        return True
    text = f"{r.title} {r.snippet}".lower()
    return any(cue in text for cue in _CONTRA_CUES)


def _confidence(surfaced: list[Result]) -> tuple[str, str]:
    if not surfaced:
        return "low", "nothing survived reranking"
    strong = sum(1 for r in surfaced if r.source_class in _STRONG_CLASSES)
    share = strong / len(surfaced)
    if share >= 0.5 and len(surfaced) >= 3:
        return "medium", "no primary-source contradiction retrieved yet"
    if share >= 0.25:
        return "low", "thin primary coverage; leans on secondary and community"
    return "low", "top results are discovery-tier, not terminal evidence"


def render(mission: Mission, reranked: list[Result], *, top: int = 6,
          retrieved: int = 0, generated_at: str = "") -> Briefing:
    surfaced = reranked[:top]
    novel_domains = sorted({r.domain for r in surfaced if r.novel_domain})
    contra = [r for r in surfaced if _is_contradicting(r)]
    fresh = [
        r for r in surfaced
        if not r.seen_before
        and r not in contra
        and "near_duplicate_content" not in r.penalties  # never present a near-dupe as new
    ]

    lines: list[str] = []

    # Bottom line
    if not surfaced:
        lines.append("## Bottom line\n")
        lines.append(
            "Nothing material surfaced for this mission. Either the query family "
            "is too narrow or the source classes asked for do not cover this "
            "question yet.\n"
        )
        body = "\n".join(lines)
        return Briefing(mission.id, generated_at, body, retrieved, 0, 0)

    lead = surfaced[0]
    lines.append("## Bottom line\n")
    lines.append(
        f"{mission.objective.rstrip('.')}. Strongest signal so far: "
        f"\"{lead.title}\" ({lead.domain}, {lead.source_class}).\n"
    )

    # What is new
    lines.append("## What is new\n")
    if fresh:
        for r in fresh:
            why = r.snippet.strip() or "no snippet"
            lines.append(
                f"- **{r.title}** — {r.domain} ({r.source_class}). {why}"
            )
    else:
        lines.append("- Nothing here is new relative to research memory.")
    lines.append("")

    # What contradicts it
    lines.append("## What contradicts it\n")
    if contra:
        for r in contra:
            lines.append(
                f"- **{r.title}** — {r.domain} ({r.source_class}). "
                f"{r.snippet.strip() or 'no snippet'}"
            )
    else:
        lines.append("No disconfirming evidence surfaced.")
    lines.append("")

    # Confidence
    level, gap = _confidence(surfaced)
    lines.append("## Confidence\n")
    lines.append(f"{level} — {gap}.\n")

    # Next question
    lines.append("## Next question\n")
    lines.append(
        f"Test the success condition directly: {mission.success_condition.rstrip('.')}. "
        f"Pursue via the adjacent-field angle if the next run is still thin.\n"
    )

    # Footer
    lines.append(
        f"_retrieved {retrieved} · surfaced {len(surfaced)} · "
        f"novel domains {len(novel_domains)} · adaptation applied: none_"
    )

    body = "\n".join(lines)
    return Briefing(
        mission_id=mission.id,
        generated_at=generated_at,
        body=body,
        retrieved=retrieved,
        surfaced=len(surfaced),
        novel_domains=len(novel_domains),
    )


_SYSTEM = """\
You write a research briefing that supports a decision. You are given a
mission and a reranked, source-classified result set. Obey every rule:

- Output GitHub-flavoured Markdown. No preamble, no restating the mission,
  no closing offer of help.
- Sections, in this order and with these headings:
  ## Bottom line   -- one or two sentences: the answer, or the state of it.
  ## What is new   -- only material not already in memory (items marked
                      seen_before=yes are NOT new). Each: the finding, the
                      source with its class in parentheses, why it matters
                      for the stated decision.
  ## What contradicts it  -- the disconfirming evidence. If none, write
                      exactly "No disconfirming evidence surfaced." Never omit
                      this section.
  ## Confidence    -- high | medium | low, and the specific gap.
  ## Next question -- the single strongest follow-up and which angle pursues it.
- Every claim carries an inline source with its class label, e.g.
  "(arxiv.org, primary)".
- Lead with what changed or is newly known, never with background.
- An aggregator or community item may only support a claim alongside a
  stronger-class source for the same point.
- Prefer one mechanism the reader can act on over five facts they cannot.
- If two strong sources disagree, present the disagreement; do not resolve it.
- 250-400 words of body. If nothing material was found, say so in two
  sentences and stop -- do not manufacture significance.
- Flat and declarative. No enthusiasm, no "it is important to note".
Do not write the footer line; it is appended mechanically."""


def _result_block(results: list[Result]) -> str:
    lines = []
    for i, r in enumerate(results, start=1):
        flags = []
        if r.seen_before:
            flags.append("seen_before=yes")
        if r.novel_domain:
            flags.append("novel_domain=yes")
        if _is_contradicting(r):
            flags.append("reads_as_disconfirming=yes")
        lines.append(
            f"{i}. {r.title}\n"
            f"   url: {r.canonical_url or r.url}\n"
            f"   domain/class: {r.domain} / {r.source_class} "
            f"(signal: {r.class_signal}, score: {r.final_score})\n"
            f"   {'; '.join(flags) if flags else 'no flags'}\n"
            f"   snippet: {r.snippet.strip() or '(none)'}"
        )
    return "\n".join(lines)


def synthesize(
    mission: Mission,
    reranked: list[Result],
    *,
    top: int = 6,
    retrieved: int = 0,
    generated_at: str = "",
    provider: str | None = None,
    model: str | None = None,
    _transport=None,
) -> Briefing:
    """LLM narrative over the reranked set, obeying prompts/briefing-agent.md.

    Falls through to the provider layer in llm.py; raises llm.LLMKeyMissing if
    no key is configured. The footer is appended deterministically so its
    counts are always accurate regardless of what the model wrote.
    """
    surfaced = reranked[:top]
    novel_domains = sorted({r.domain for r in surfaced if r.novel_domain})

    user = (
        f"MISSION\n"
        f"objective: {mission.objective}\n"
        f"success condition: {mission.success_condition}\n"
        f"target source classes: {', '.join(mission.target_classes) or 'any'}\n"
        f"novelty requirement: {mission.novelty_requirement}\n\n"
        f"RESULTS (already reranked, best first)\n{_result_block(surfaced)}\n"
    )

    body = llm.synthesize(
        _SYSTEM, user, provider=provider, model=model, _transport=_transport
    ).rstrip()

    footer = (
        f"\n\n_retrieved {retrieved} · surfaced {len(surfaced)} · "
        f"novel domains {len(novel_domains)} · adaptation applied: none_"
    )
    return Briefing(
        mission_id=mission.id,
        generated_at=generated_at,
        body=body + footer,
        retrieved=retrieved,
        surfaced=len(surfaced),
        novel_domains=len(novel_domains),
    )
