"""CLI entry point.

    python -m research_os run --mission missions/example-tennis-features.yaml
    python -m research_os run --mission M.yaml --connector brave --top 6
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import load_mission, run_mission

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # briefings use em dashes
    except (AttributeError, ValueError):
        pass


def _cmd_run(args: argparse.Namespace) -> int:
    mission = load_mission(args.mission)
    out = run_mission(
        mission,
        connector=args.connector,
        limit=args.limit,
        top=args.top,
        db_path=args.db,
    )
    print(out.briefing.body)
    print()
    print(f"[{out.mission.id}] {out.retrieved} retrieved -> "
          f"{out.briefing.surfaced} surfaced -> memory: {args.db}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research-os", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run one mission end to end")
    run.add_argument("--mission", required=True, help="path to a mission YAML")
    run.add_argument("--connector", default="fixture",
                     help="fixture (default, offline) or brave")
    run.add_argument("--limit", type=int, default=10, help="results per query")
    run.add_argument("--top", type=int, default=6, help="results surfaced in the briefing")
    run.add_argument("--db", default="research-memory.sqlite", help="SQLite memory path")
    run.set_defaults(func=_cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
