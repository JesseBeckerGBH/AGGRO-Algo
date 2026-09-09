"""Turn a mission into a query family.

Deterministic stand-in for the LLM Mission Planner (prompts/mission-planner.md).
It reads angle definitions and the per-novelty angle set from
configs/query-families.yaml and fills the templates from mission fields.
Minimum three angles; disconfirming + adjacent_field forced on medium/high
novelty so the system cannot build a well-sourced echo chamber.
"""

from __future__ import annotations

import datetime as _dt

from .config import angle_set, query_families
from .models import Mission, Query

_FORCED_ON_NOVELTY = {"medium", "high"}
_FORCED_ANGLES = ("disconfirming", "adjacent_field")


def _fill(template: str, mission: Mission) -> str:
    seeds = mission.vocabulary_seed or [mission.objective]
    topic = seeds[0]
    technical_term = seeds[0]
    qualifier = seeds[1] if len(seeds) > 1 else ""
    subs = {
        "topic": topic,
        "technical_term": technical_term,
        "qualifier": qualifier,
        "structural_problem": topic,
        "adjacent_domain": "another quantitative field",
        "current_year": str(_dt.date.today().year),
    }
    out = template
    for k, v in subs.items():
        out = out.replace("{" + k + "}", v)
    return " ".join(out.split())


def plan(mission: Mission) -> list[Query]:
    qf = query_families()
    angles = qf.get("angles", {})
    chosen = angle_set(mission.novelty_requirement)

    if mission.novelty_requirement in _FORCED_ON_NOVELTY:
        for a in _FORCED_ANGLES:
            if a not in chosen and a in angles:
                chosen.append(a)

    queries: list[Query] = []
    for name in chosen:
        spec = angles.get(name)
        if not spec:
            continue
        text = _fill(spec.get("template", "{topic}"), mission)
        if not text:
            continue
        queries.append(
            Query(angle=name, text=text, expected_source_class="")
        )

    if len(queries) < 3:  # min_angles_per_mission
        raise ValueError(
            f"mission {mission.id!r} produced only {len(queries)} queries; "
            f"need >= 3 structurally different angles"
        )
    return queries
