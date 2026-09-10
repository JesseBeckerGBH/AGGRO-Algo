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
from . import canonical, classify, llm, novelty, planning, rerank, telemetry
from .connectors import get_connectors
from .models import Briefing, Mission, Result
from .memory import Memory
from .telemetry import DriftReport


@dataclass
class RunOutput:
    mission: Mission
    briefing: Briefing
    reranked: list[Result]
    retrieved: int
    per_connector: dict[str, int] = None  # type: ignore[assignment]
    novelty_yield: float = 0.0
    domain_top_share: float = 0.0
    new_vocab: list[str] = None  # type: ignore[assignment]
    failures: list[dict] = None  # type: ignore[assignment]
    drift: DriftReport = None  # type: ignore[assignment]


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
    brief_mode: str = "render",  # render | llm | auto
    llm_provider: str | None = None,
    llm_model: str | None = None,
) -> RunOutput:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conns = get_connectors(connector)

    # Stage 4: fold operator-promoted vocabulary back into the mission before
    # planning (query-families.yaml: vocabulary_escalation).
    with Memory(db_path) as _m:
        for term in _m.promoted_terms(mission.id):
            if term.lower() not in {s.lower() for s in mission.vocabulary_seed}:
                mission.vocabulary_seed.append(term)

    queries = planning.plan(mission)

    collected: list[Result] = []
    per_connector: dict[str, int] = {c.name: 0 for c in conns}
    with Memory(db_path) as mem:
        mem.upsert_mission(mission, now)

        connector_errors: dict[str, tuple[str, str]] = {}
        for q in queries:
            for conn in conns:
                try:
                    hits = conn.search(q.text, limit=limit)
                except Exception as exc:  # a dead connector must not kill the run
                    connector_errors[conn.name] = (
                        type(exc).__name__, str(exc)[:200]
                    )
                    mem.record_query(mission.id, q, conn.name, now, 0)
                    continue
                for h in hits:
                    h.query_angle = q.angle
                qid = mem.record_query(mission.id, q, conn.name, now, len(hits))
                for h in hits:
                    h._query_id = qid  # type: ignore[attr-defined]
                per_connector[conn.name] += len(hits)
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
        prior_shares, prior_top = mem.domain_shares(mission.id)  # state BEFORE this run
        novelty.score(deduped, prior_shares)
        ordered = rerank.rerank(deduped, mission)

        mode = brief_mode
        if mode == "auto":
            mode = "llm" if llm.available_provider() else "render"
        if mode == "llm":
            brief = briefing_mod.synthesize(
                mission, ordered, top=top, retrieved=retrieved, generated_at=now,
                provider=llm_provider, model=llm_model,
            )
        else:
            brief = briefing_mod.render(
                mission, ordered, top=top, retrieved=retrieved, generated_at=now
            )

        surfaced = ordered[:top]
        n_yield = novelty.yield_of(surfaced)
        p_share = (
            sum(1 for r in surfaced if r.source_class == "primary") / len(surfaced)
            if surfaced else 0.0
        )
        d_share = (
            sum(1 for r in surfaced
                if r.query_angle == "disconfirming" or briefing_mod._is_contradicting(r))
            / len(surfaced) if surfaced else 0.0
        )

        # persist the deduped+scored set and the briefing
        by_qid: dict[int, list[Result]] = {}
        for r in ordered:
            by_qid.setdefault(getattr(r, "_query_id", 0), []).append(r)
        for qid, rows in by_qid.items():
            mem.record_results(mission.id, qid or None, rows)
        mem.record_briefing(brief, novelty_yield=n_yield,
                            primary_share=p_share, disconfirming_share=d_share)

        # Stage 4: update concentration + harvest vocabulary AFTER scoring this run
        mem.record_domain_hits(mission.id, ordered, now)
        new_vocab = mem.harvest_vocab(
            mission.id, ordered, mission.vocabulary_seed, now
        )
        _, top_share = mem.domain_shares(mission.id)

        # Stage 6: classify + log this run's failures, then run the drift check
        failures = telemetry.detect_failures(
            mission, surfaced, brief,
            connector_errors=connector_errors, retrieved=retrieved,
        )
        mem.record_failures(mission.id, failures, now)
        drift = telemetry.check_drift(mission.id, mem)
        mem.record_drift_check(
            mission.id, now, drift.metrics, [name for name, _ in drift.breaches]
        )

    return RunOutput(
        mission=mission, briefing=brief, reranked=ordered,
        retrieved=retrieved, per_connector=per_connector,
        novelty_yield=n_yield, domain_top_share=top_share, new_vocab=new_vocab,
        failures=failures, drift=drift,
    )
