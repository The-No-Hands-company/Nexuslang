#!/usr/bin/env python3
"""Quick parser performance smoke test for CI."""

import argparse
import json
import sys
import time
from pathlib import Path

from nlpl.parser.ast_cache import get_global_cache
from nlpl.parser.cached_parser import parse_with_cache


def measure_parse_ms(file_path: Path) -> float:
    """Measure cold parse time for a file in milliseconds."""
    text = file_path.read_text(encoding="utf-8")
    cache = get_global_cache()
    cache.clear()
    start = time.perf_counter()
    parse_with_cache(file_path.as_uri(), text, debug=False)
    return (time.perf_counter() - start) * 1000


def load_baseline(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {k: float(v) for k, v in data.get("results", {}).items()}
    except Exception:  # noqa: BLE001
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NLPL perf smoke")
    parser.add_argument("--sample", action="append", default=[], help="Sample NLPL file (repeatable)")
    parser.add_argument("--threshold-ms", type=float, default=1500.0, help="Maximum allowed parse time per sample")
    parser.add_argument("--baseline", type=Path, default=Path("perf-baseline.json"), help="Optional baseline JSON to compare")
    parser.add_argument("--tolerance", type=float, default=0.15, help="Allowed regression vs baseline (fraction)")
    parser.add_argument("--output", type=Path, default=Path("perf-smoke.json"), help="Output report path")
    args = parser.parse_args()

    samples = [Path(p) for p in (args.sample or [])] or [
        Path("examples/01_basic_concepts.nlpl"),
        Path("examples/24_struct_and_union.nlpl"),
    ]

    missing = [str(p) for p in samples if not p.exists()]
    if missing:
        print(f"Missing samples: {', '.join(missing)}", file=sys.stderr)
        return 1

    baseline = load_baseline(args.baseline)
    results: dict[str, float] = {}
    failures: list[str] = []

    for sample in samples:
        elapsed_ms = measure_parse_ms(sample)
        results[str(sample.resolve())] = round(elapsed_ms, 2)
        if elapsed_ms > args.threshold_ms:
            failures.append(
                f"{sample.name}: {elapsed_ms:.1f}ms > threshold {args.threshold_ms:.1f}ms"
            )
        if baseline:
            base = baseline.get(str(sample.resolve()), baseline.get(sample.name))
            if base:
                allowed = base * (1 + args.tolerance)
                if elapsed_ms > allowed:
                    failures.append(
                        f"{sample.name}: {elapsed_ms:.1f}ms > baseline {base:.1f}ms * (1+{args.tolerance:.2f})"
                    )

    report = {
        "threshold_ms": args.threshold_ms,
        "tolerance": args.tolerance,
        "baseline": baseline,
        "results": results,
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if failures:
        for item in failures:
            print(f"FAIL: {item}", file=sys.stderr)
        return 1

    print("Perf smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
