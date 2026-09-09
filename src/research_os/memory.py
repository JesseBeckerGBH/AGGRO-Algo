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
    novelty_yield   REAL,
    usefulness_rating TEXT
);
-- Stage 4: per-mission domain concentration.
CREATE TABLE IF NOT EXISTS mission_domains (
    mission_id  TEXT NOT NULL REFERENCES missions(mission_id),
    domain      TEXT NOT NULL,
    hits        INTEGER NOT NULL DEFAULT 0,
    first_seen  TEXT,
    last_seen   TEXT,
    PRIMARY KEY (mission_id, domain)
);
-- Stage 4: promoted-vocabulary store. Terms harvested from primary-class
-- results; status starts 'candidate' and only the operator moves it to
-- 'promoted' (query-families.yaml: operator_confirms_before_promotion).
CREATE TABLE IF NOT EXISTS promoted_vocab (
    mission_id       TEXT NOT NULL REFERENCES missions(mission_id),
    term             TEXT NOT NULL,
    distinct_sources INTEGER NOT NULL DEFAULT 0,
    status           TEXT NOT NULL DEFAULT 'candidate',  -- candidate | promoted | rejected
    first_seen       TEXT,
    decided_at       TEXT,
    PRIMARY KEY (mission_id, term)
);
"""

# generic words that are never worth promoting as vocabulary
_VOCAB_STOP = {
    "the", "and", "for", "with", "from", "that", "this", "these", "those", "into",
    "using", "based", "model", "models", "data", "results", "paper", "study",
    "match", "matches", "player", "players", "tennis", "prediction", "predictive",
    "features", "feature", "outcome", "outcomes", "analysis", "approach", "method",
    "methods", "new", "how", "why", "are", "was", "were", "has", "have", "can",
    "which", "their", "our", "its", "such", "also", "more", "most", "than", "then",
    "learning", "machine", "neural", "network", "networks", "training", "test",
    "dataset", "datasets", "accuracy", "performance", "research", "work", "used",
    "different", "various", "propose", "proposed", "show", "shows", "result",
    # function words + prose glue that bigram harvesting otherwise captures
    "they", "them", "when", "where", "while", "about", "into", "over", "under",
    "moreover", "furthermore", "however", "thus", "hence", "here", "there",
    "developed", "extracted", "including", "generated", "suggest", "suggests",
    "identifying", "identify", "surpassing", "improve", "improved", "improvement",
    "alone", "well", "both", "each", "some", "many", "will", "would", "could",
    "one", "two", "three", "first", "second", "may", "might", "must", "been",
    "get", "got", "make", "made", "use", "uses", "via", "per", "not",
}
# bigrams that clear the threshold but carry no domain-specific signal
_VOCAB_STOP_PHRASES = {
    "machine learning", "deep learning", "logistic regression", "linear regression",
    "random forest", "gradient boosting", "cross validation", "feature selection",
    "feature engineering", "data set", "test set", "training set", "related work",
    "state art", "high accuracy", "prediction model", "predictive model",
}


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
        priors = {
            row["domain"]: row["hits"]
            for row in self.conn.execute(
                "SELECT domain, hits FROM mission_domains WHERE mission_id = ?",
                (mission_id,),
            )
        }
        for r in results:
            row = self.conn.execute(
                "SELECT 1 FROM results WHERE content_hash = ? OR canonical_url = ? LIMIT 1",
                (r.content_hash, r.canonical_url),
            ).fetchone()
            r.seen_before = row is not None
            r.domain_prior_hits = priors.get(r.domain, 0)
            r.novel_domain = r.domain_prior_hits == 0
        return results

    def domain_shares(self, mission_id: str) -> tuple[dict[str, float], float]:
        rows = list(self.conn.execute(
            "SELECT domain, hits FROM mission_domains WHERE mission_id = ?", (mission_id,)
        ))
        total = sum(row["hits"] for row in rows)
        if not total:
            return {}, 0.0
        shares = {row["domain"]: row["hits"] / total for row in rows}
        return shares, max(shares.values())

    def record_domain_hits(self, mission_id: str, results: list[Result], now: str) -> None:
        counts: dict[str, int] = {}
        for r in results:
            if r.domain:
                counts[r.domain] = counts.get(r.domain, 0) + 1
        for domain, n in counts.items():
            self.conn.execute(
                "INSERT INTO mission_domains (mission_id, domain, hits, first_seen, last_seen) "
                "VALUES (?,?,?,?,?) "
                "ON CONFLICT(mission_id, domain) DO UPDATE SET "
                "hits = hits + excluded.hits, last_seen = excluded.last_seen",
                (mission_id, domain, n, now, now),
            )
        self.conn.commit()

    # -- promoted vocabulary -------------------------------------------
    def harvest_vocab(self, mission_id: str, results: list[Result],
                      operator_terms: list[str], now: str, *, threshold: int = 2,
                      cap: int = 10) -> list[str]:
        """Harvest candidate domain terms from the TITLES of primary-class
        results returned by the primary_source_hunt angle (query-families.yaml:
        vocabulary_escalation). A bigram appearing in `threshold`+ distinct
        primary sources becomes a 'candidate' — never auto-promoted. At most
        `cap` new candidates per run, highest source-count first."""
        import re

        have = {t.lower() for t in operator_terms}
        pool = [r for r in results if r.source_class == "primary"]

        # term -> set of distinct primary SOURCES (documents) it appeared in.
        # Titles only: they are short and term-dense; snippet prose floods the
        # harvest with glue bigrams ("they extracted", "moreover gao").
        seen: dict[str, set[str]] = {}
        for r in pool:
            source_id = r.canonical_url or r.url or r.content_hash
            title = re.sub(r"[·|–—-]\s*github.*$", "", r.title.lower())
            words = re.findall(r"[a-z][a-z0-9+-]{2,}", title)
            for a, b in zip(words, words[1:]):
                if a in _VOCAB_STOP or b in _VOCAB_STOP or len(a) < 3 or len(b) < 3:
                    continue
                term = f"{a} {b}"
                if term in have or term in _VOCAB_STOP_PHRASES:
                    continue
                seen.setdefault(term, set()).add(source_id)

        ranked = sorted(
            ((t, s) for t, s in seen.items() if len(s) >= threshold),
            key=lambda kv: (-len(kv[1]), kv[0]),
        )[:cap]

        new_candidates: list[str] = []
        for term, sources in ranked:
            row = self.conn.execute(
                "SELECT status, distinct_sources FROM promoted_vocab "
                "WHERE mission_id = ? AND term = ?", (mission_id, term),
            ).fetchone()
            if row is None:
                self.conn.execute(
                    "INSERT INTO promoted_vocab (mission_id, term, distinct_sources, "
                    "status, first_seen) VALUES (?,?,?,'candidate',?)",
                    (mission_id, term, len(sources), now),
                )
                new_candidates.append(term)
            elif row["status"] == "candidate":
                self.conn.execute(
                    "UPDATE promoted_vocab SET distinct_sources = MAX(distinct_sources, ?) "
                    "WHERE mission_id = ? AND term = ?", (len(sources), mission_id, term),
                )
        self.conn.commit()
        return new_candidates

    def list_vocab(self, mission_id: str, status: str | None = None) -> list[sqlite3.Row]:
        sql = ("SELECT term, distinct_sources, status, first_seen, decided_at "
               "FROM promoted_vocab WHERE mission_id = ?")
        args: list = [mission_id]
        if status:
            sql += " AND status = ?"
            args.append(status)
        sql += " ORDER BY distinct_sources DESC, term"
        return list(self.conn.execute(sql, args))

    def set_vocab_status(self, mission_id: str, term: str, status: str, now: str) -> bool:
        cur = self.conn.execute(
            "UPDATE promoted_vocab SET status = ?, decided_at = ? "
            "WHERE mission_id = ? AND term = ?", (status, now, mission_id, term.lower()),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def promoted_terms(self, mission_id: str) -> list[str]:
        return [row["term"] for row in self.conn.execute(
            "SELECT term FROM promoted_vocab WHERE mission_id = ? AND status = 'promoted' "
            "ORDER BY term", (mission_id,),
        )]

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

    def record_briefing(self, b: Briefing, novelty_yield: float = 0.0) -> int:
        cur = self.conn.execute(
            "INSERT INTO briefings (mission_id, generated_at, body, retrieved, "
            "surfaced, novel_domains, novelty_yield) VALUES (?,?,?,?,?,?,?)",
            (b.mission_id, b.generated_at, b.body, b.retrieved, b.surfaced,
             b.novel_domains, novelty_yield),
        )
        self.conn.commit()
        return int(cur.lastrowid)
