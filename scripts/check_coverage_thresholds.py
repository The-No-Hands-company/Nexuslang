#!/usr/bin/env python3
"""
scripts/check_coverage_thresholds.py

Reads coverage.json produced by pytest-cov and enforces per-component
minimum coverage thresholds. Exits with code 1 if any threshold is missed.

Usage:
    python scripts/check_coverage_thresholds.py [--json coverage.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Thresholds (percent, float)
# These mirror the roadmap targets from 8.4.1
# ---------------------------------------------------------------------------
COMPONENT_THRESHOLDS: Dict[str, Tuple[str, float]] = {
    "src/nlpl/parser": ("Parser & Lexer", 85.0),
    "src/nlpl/interpreter": ("Interpreter", 80.0),
    "src/nlpl/stdlib": ("Standard Library", 80.0),
    "src/nlpl/typesystem": ("Type System", 75.0),
    "src/nlpl/runtime": ("Runtime", 75.0),
}

GLOBAL_THRESHOLD: float = 80.0


def _normalise_path(p: str) -> str:
    """Convert backslashes to forward slashes and strip leading ./"""
    return p.replace("\\", "/").lstrip("./")


def _load_coverage(json_path: Path) -> dict:
    with json_path.open() as fh:
        return json.load(fh)


def _component_stats(
    files: dict,
) -> Dict[str, Tuple[int, int]]:
    """Return {component_prefix: (covered_lines, total_lines)}."""
    stats: Dict[str, Tuple[int, int]] = {}
    for fname, data in files.items():
        fn = _normalise_path(fname)
        for prefix in COMPONENT_THRESHOLDS:
            norm_prefix = _normalise_path(prefix)
            if fn.startswith(norm_prefix):
                covered, total = stats.get(prefix, (0, 0))
                summary = data.get("summary", {})
                covered += summary.get("covered_lines", 0)
                total += summary.get("num_statements", 0)
                stats[prefix] = (covered, total)
                break
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enforce per-component coverage thresholds."
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default="coverage.json",
        help="Path to coverage.json (default: coverage.json)",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Print results but do not exit non-zero on failure",
    )
    args = parser.parse_args(argv)

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"[coverage-check] ERROR: {json_path} not found.", file=sys.stderr)
        print(
            "  Run: pytest tests/ --cov=src/nlpl --cov-report=json",
            file=sys.stderr,
        )
        return 1 if not args.no_fail else 0

    data = _load_coverage(json_path)
    files: dict = data.get("files", {})
    total_summary = data.get("totals", {})

    global_pct: float = total_summary.get("percent_covered", 0.0)
    component_stats = _component_stats(files)

    # ---------------------------------------------------------------------------
    # Print report
    # ---------------------------------------------------------------------------
    COL_W = 30
    print()
    print("=" * 70)
    print("Coverage threshold report")
    print("=" * 70)
    print(f"{'Component':<{COL_W}} {'Coverage':>10}  {'Threshold':>10}  {'Pass':>6}")
    print("-" * 70)

    failures: list[str] = []

    for prefix, (label, threshold) in COMPONENT_THRESHOLDS.items():
        covered, total = component_stats.get(prefix, (0, 0))
        if total == 0:
            pct = 0.0
            note = " (no files found)"
        else:
            pct = 100.0 * covered / total
            note = ""
        ok = pct >= threshold
        status = "OK" if ok else "FAIL"
        print(
            f"{label:<{COL_W}} {pct:>9.1f}%  {threshold:>9.1f}%  {status:>6}{note}"
        )
        if not ok:
            failures.append(
                f"{label}: {pct:.1f}% < {threshold:.1f}% (short by {threshold - pct:.1f}pp)"
            )

    print("-" * 70)
    global_ok = global_pct >= GLOBAL_THRESHOLD
    global_status = "OK" if global_ok else "FAIL"
    print(
        f"{'TOTAL (all src/nlpl)':<{COL_W}} {global_pct:>9.1f}%  "
        f"{GLOBAL_THRESHOLD:>9.1f}%  {global_status:>6}"
    )
    print("=" * 70)

    if not global_ok:
        failures.append(
            f"GLOBAL: {global_pct:.1f}% < {GLOBAL_THRESHOLD:.1f}% "
            f"(short by {GLOBAL_THRESHOLD - global_pct:.1f}pp)"
        )

    if failures:
        print()
        print("[coverage-check] FAILED - thresholds not met:")
        for msg in failures:
            print(f"  - {msg}")
        print()
        return 0 if args.no_fail else 1

    print()
    print("[coverage-check] All thresholds met.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
