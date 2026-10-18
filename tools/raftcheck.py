#!/usr/bin/env python3
"""raftcheck -- replay seeded Raft schedules and machine-check safety.

Implemented in the golden patch. The scaffold parses the graded CLI
contract (``--seed`` / ``--count`` / ``--trace`` / ``--steps``) so the
entrypoint shape is stable; the explorer itself exits ``2`` until the
protocol it drives exists.
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="raftcheck",
        description=(
            "Replay seeded message/timer schedules against the raftsim "
            "cluster and machine-check Election Safety, Log Matching, "
            "Leader Completeness and State Machine Safety."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="first schedule seed to explore (default: 0)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1500,
        help="how many consecutive seeds to explore (default: 1500)",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="print the per-tick schedule trace for failing seeds",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=400,
        help="virtual-clock ticks simulated per schedule (default: 400)",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.count < 0 or args.steps <= 0:
        print("raftcheck: --count and --steps must be non-negative/positive",
              file=sys.stderr)
        return 2
    print("raftcheck: schedule explorer not implemented", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
