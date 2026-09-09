"""CLI entry point.

    python -m research_os run --mission missions/example-tennis-features.yaml
    python -m research_os run --mission M.yaml --connector brave --top 6
"""

from __future__ import annotations

import argparse
import sys

from .llm import LLMError, LLMKeyMissing
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
    print(
        f"[{out.mission.id}] retrieved {out.retrieved} ({per_conn}) -> "
        f"{out.briefing.surfaced} surfaced\n"
        f"  domains: {len(surfaced_domains)} in briefing / {len(pool_domains)} in pool\n"
        f"  memory: {args.db}",
        file=sys.stderr,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research-os", description=__doc__)
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
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
