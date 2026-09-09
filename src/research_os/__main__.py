"""CLI entry point.

    python -m research_os run   --mission missions/example-tennis-features.yaml
    python -m research_os run   --mission M.yaml --connector brave,marginalia --brief llm
    python -m research_os vocab --mission M.yaml                 # review harvested terms
    python -m research_os vocab --mission M.yaml --promote "serve rates" --reject "grand slam"
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from .llm import LLMError, LLMKeyMissing
from .memory import Memory
from .pipeline import load_mission, run_mission

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # briefings use em dashes
    except (AttributeError, ValueError):
        pass


def _cmd_run(args: argparse.Namespace) -> int:
    mission = load_mission(args.mission)
    try:
        out = run_mission(
            mission,
            connector=args.connector,
            limit=args.limit,
            top=args.top,
            db_path=args.db,
            brief_mode=args.brief,
            llm_provider=args.llm_provider,
            llm_model=args.llm_model,
        )
    except LLMKeyMissing as e:
        print(f"error: {e}\nhint: cp .env.example .env and add a key, or use "
              f"--brief render / --brief auto", file=sys.stderr)
        return 2
    except LLMError as e:
        print(f"error: LLM synthesis failed: {e}", file=sys.stderr)
        return 2
    print(out.briefing.body)
    print()

    surfaced_domains = {r.domain for r in out.reranked[: out.briefing.surfaced]}
    pool_domains = {r.domain for r in out.reranked}
    per_conn = ", ".join(f"{k}={v}" for k, v in (out.per_connector or {}).items())
    lines = [
        f"[{out.mission.id}] retrieved {out.retrieved} ({per_conn}) -> "
        f"{out.briefing.surfaced} surfaced",
        f"  domains: {len(surfaced_domains)} in briefing / {len(pool_domains)} in pool"
        f"  |  top-domain share (memory): {out.domain_top_share:.0%}",
        f"  novelty yield: {out.novelty_yield:.0%}"
        + ("   [below 20% floor]" if out.novelty_yield < 0.20 else ""),
        f"  memory: {args.db}",
    ]
    if out.new_vocab:
        shown = ", ".join(f'"{t}"' for t in out.new_vocab[:6])
        more = f" (+{len(out.new_vocab) - 6} more)" if len(out.new_vocab) > 6 else ""
        lines.append(f"  {len(out.new_vocab)} new vocab candidate(s): {shown}{more}")
        lines.append(f"  review: research-os vocab --mission {args.mission} --db {args.db}")
    print("\n".join(lines), file=sys.stderr)
    return 0


def _cmd_vocab(args: argparse.Namespace) -> int:
    mission = load_mission(args.mission)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with Memory(args.db) as mem:
        for term in args.promote or []:
            ok = mem.set_vocab_status(mission.id, term, "promoted", now)
            print(f"{'promoted' if ok else 'not found'}: {term!r}", file=sys.stderr)
        for term in args.reject or []:
            ok = mem.set_vocab_status(mission.id, term, "rejected", now)
            print(f"{'rejected' if ok else 'not found'}: {term!r}", file=sys.stderr)

        rows = mem.list_vocab(mission.id, status=args.status)
        if not rows:
            print("(no vocabulary terms recorded for this mission yet)")
            return 0
        print(f"{'STATUS':<10} {'SRCS':>4}  TERM")
        for r in rows:
            print(f"{r['status']:<10} {r['distinct_sources']:>4}  {r['term']}")
        promoted = [r["term"] for r in rows if r["status"] == "promoted"]
        if promoted:
            print(f"\nfed as vocabulary_seed on the next run: {', '.join(promoted)}",
                  file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research-os", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run one mission end to end")
    run.add_argument("--mission", required=True, help="path to a mission YAML")
    run.add_argument("--connector", default="fixture",
                     help="one or a comma-list: fixture (offline), brave, marginalia "
                          "— e.g. --connector brave,marginalia")
    run.add_argument("--limit", type=int, default=10, help="results per query")
    run.add_argument("--top", type=int, default=6, help="results surfaced in the briefing")
    run.add_argument("--db", default="research-memory.sqlite", help="SQLite memory path")
    run.add_argument("--brief", choices=("render", "llm", "auto"), default="render",
                     help="render = deterministic (default); llm = LLM synthesis; "
                          "auto = llm if a key is configured, else render")
    run.add_argument("--llm-provider", default=None,
                     help="gemini | anthropic | openai (else $LLM_PROVIDER, else gemini)")
    run.add_argument("--llm-model", default=None, help="override the provider default model")
    run.set_defaults(func=_cmd_run)

    voc = sub.add_parser("vocab", help="review / promote harvested vocabulary")
    voc.add_argument("--mission", required=True, help="path to the mission YAML")
    voc.add_argument("--db", default="research-memory.sqlite", help="SQLite memory path")
    voc.add_argument("--status", choices=("candidate", "promoted", "rejected"),
                     default=None, help="filter the listing")
    voc.add_argument("--promote", action="append", metavar="TERM",
                     help="mark a term promoted (repeatable) — fed as vocabulary_seed next run")
    voc.add_argument("--reject", action="append", metavar="TERM",
                     help="mark a term rejected (repeatable)")
    voc.set_defaults(func=_cmd_vocab)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
