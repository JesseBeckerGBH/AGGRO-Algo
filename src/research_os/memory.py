"""Persistent research memory (SQLite).

Without memory the system cannot tell discovery from repetition. Schema is the
Stage-2 subset of docs/memory/sqlite-schema.md: missions, queries, results,
briefings. failure_events / adaptation_events arrive with Stage 6-7.

Novelty is decided here, before rerank: a result is `seen_before` if its
content hash or canonical URL is already stored; its domain is `novel_domain`
if this mission has never stored that domain.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import Briefing, Mission, Query, Result

_SCHEMA = """
CREATE TABLE IF NOT EXISTS missions (
    mission_id      TEXT PRIMARY KEY,
    objective       TEXT NOT NULL,
    success_condition TEXT NOT NULL,
    novelty_requirement TEXT,
    first_run_at    TEXT,
    last_run_at     TEXT
);
CREATE TABLE IF NOT EXISTS queries (
    query_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id   TEXT NOT NULL REFERENCES missions(mission_id),
    angle        TEXT,
    query_text   TEXT NOT NULL,
    executed_at  TEXT,
    connector    TEXT,
    result_count INTEGER
);
CREATE TABLE IF NOT EXISTS results (
    result_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id     TEXT NOT NULL REFERENCES missions(mission_id),
    query_id       INTEGER REFERENCES queries(query_id),
    connector      TEXT,
    title          TEXT,
    url            TEXT,
    canonical_url  TEXT,
    domain         TEXT,
    content_hash   TEXT,
    source_class   TEXT,
    class_signal   TEXT,
    final_score    REAL,
    retrieved_at   TEXT
);
CREATE INDEX IF NOT EXISTS ix_results_hash ON results(content_hash);
CREATE INDEX IF NOT EXISTS ix_results_canon ON results(canonical_url);
CREATE INDEX IF NOT EXISTS ix_results_mission_domain ON results(mission_id, domain);
CREATE TABLE IF NOT EXISTS briefings (
    briefing_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id      TEXT NOT NULL REFERENCES missions(mission_id),
    generated_at    TEXT,
    body            TEXT,
    retrieved       INTEGER,
    surfaced        INTEGER,
    novel_domains   INTEGER,
    usefulness_rating TEXT
);
"""


class Memory:
    def __init__(self, path: str | Path = "research-memory.sqlite"):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Memory":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- mission -----------------------------------------------------------
    def upsert_mission(self, m: Mission, now: str) -> None:
        cur = self.conn.execute(
            "SELECT mission_id FROM missions WHERE mission_id = ?", (m.id,)
        )
        if cur.fetchone():
            self.conn.execute(
                "UPDATE missions SET last_run_at = ? WHERE mission_id = ?", (now, m.id)
            )
        else:
            self.conn.execute(
                "INSERT INTO missions (mission_id, objective, success_condition, "
                "novelty_requirement, first_run_at, last_run_at) VALUES (?,?,?,?,?,?)",
                (m.id, m.objective, m.success_condition, m.novelty_requirement, now, now),
            )
        self.conn.commit()

    # -- novelty ---------------------------------------------------------
    def mark_novelty(self, mission_id: str, results: list[Result]) -> list[Result]:
        for r in results:
            row = self.conn.execute(
                "SELECT 1 FROM results WHERE content_hash = ? OR canonical_url = ? LIMIT 1",
                (r.content_hash, r.canonical_url),
            ).fetchone()
            r.seen_before = row is not None
            drow = self.conn.execute(
                "SELECT 1 FROM results WHERE mission_id = ? AND domain = ? LIMIT 1",
                (mission_id, r.domain),
            ).fetchone()
            r.novel_domain = drow is None
        return results

    # -- writes --------------------------------------------------------
    def record_query(self, mission_id: str, q: Query, connector: str,
                     executed_at: str, count: int) -> int:
        cur = self.conn.execute(
            "INSERT INTO queries (mission_id, angle, query_text, executed_at, "
            "connector, result_count) VALUES (?,?,?,?,?,?)",
            (mission_id, q.angle, q.text, executed_at, connector, count),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def record_results(self, mission_id: str, query_id: int, results: list[Result]) -> None:
        self.conn.executemany(
            "INSERT INTO results (mission_id, query_id, connector, title, url, "
            "canonical_url, domain, content_hash, source_class, class_signal, "
            "final_score, retrieved_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (mission_id, query_id, r.connector, r.title, r.url, r.canonical_url,
                 r.domain, r.content_hash, r.source_class, r.class_signal,
                 r.final_score, r.retrieved_at)
                for r in results
            ],
        )
        self.conn.commit()

    def record_briefing(self, b: Briefing) -> int:
        cur = self.conn.execute(
            "INSERT INTO briefings (mission_id, generated_at, body, retrieved, "
            "surfaced, novel_domains) VALUES (?,?,?,?,?,?)",
            (b.mission_id, b.generated_at, b.body, b.retrieved, b.surfaced, b.novel_domains),
        )
        self.conn.commit()
        return int(cur.lastrowid)
