"""The vertical slice, wired end to end.

mission -> query family -> connector -> canonicalize + dedupe -> classify
-> novelty (memory) -> rerank (class before relevance) -> top K -> briefing
-> persist. One ugly path that produces one output you can actually judge
against the success test in docs/operations/implementation-order.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import briefing as briefing_mod
from . import canonical, classify, planning, rerank
from .connectors import get_connector
from .models import Briefing, Mission, Result
from .memory import Memory


@dataclass
class RunOutput:
    mission: Mission
    briefing: Briefing
    reranked: list[Result]
    retrieved: int


def load_mission(path: str | Path) -> Mission:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if "mission" in data:  # allow either a bare mapping or {mission: {...}}
        data = data["mission"]
    return Mission.from_dict(data)


def run_mission(
    mission: Mission,
    *,
    connector: str = "fixture",
    limit: int = 10,
    top: int = 6,
    db_path: str | Path = "research-memory.sqlite",
) -> RunOutput:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = get_connector(connector)
    queries = planning.plan(mission)

    collected: list[Result] = []
    with Memory(db_path) as mem:
        mem.upsert_mission(mission, now)

        for q in queries:
            hits = conn.search(q.text, limit=limit)
            for h in hits:
                h.query_angle = q.angle
            qid = mem.record_query(mission.id, q, conn.name, now, len(hits))
            for h in hits:
                h._query_id = qid  # type: ignore[attr-defined]
            collected.extend(hits)

        retrieved = len(collected)

        canonical.enrich(collected)
        deduped = canonical.dedupe(collected)
        deduped = [
            r for r in deduped
            if not any(r.domain == d or r.domain.endswith("." + d)
                       for d in mission.excluded_domains)
        ]
        classify.classify(deduped)
        mem.mark_novelty(mission.id, deduped)
        ordered = rerank.rerank(deduped, mission)

        brief = briefing_mod.render(
            mission, ordered, top=top, retrieved=retrieved, generated_at=now
        )

        # persist the deduped+scored set and the briefing
        by_qid: dict[int, list[Result]] = {}
        for r in ordered:
            by_qid.setdefault(getattr(r, "_query_id", 0), []).append(r)
        for qid, rows in by_qid.items():
            mem.record_results(mission.id, qid or None, rows)
        mem.record_briefing(brief)

    return RunOutput(mission=mission, briefing=brief, reranked=ordered, retrieved=retrieved)
