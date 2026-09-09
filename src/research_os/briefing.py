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


def synthesize(mission: Mission, reranked: list[Result]) -> str:
    """Seam for LLM narrative synthesis. Not implemented in the slice."""
    raise NotImplementedError(
        "LLM briefing synthesis is the step after the vertical slice passes "
        "its success test — see docs/operations/implementation-order.md Stage 2."
    )
