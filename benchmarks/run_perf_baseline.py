"""
NLPL Performance Baseline Runner
==================================

Measures interpreter performance across multiple benchmark programs
and compares to C reference implementations. Produces perf-baseline.json
with NLPL-vs-C ratios and optimization-level comparisons.

Usage:
    python benchmarks/run_perf_baseline.py
    python benchmarks/run_perf_baseline.py --output perf-baseline.json
    python benchmarks/run_perf_baseline.py --runs 20 --verbose

Output format (perf-baseline.json):
{
    "meta": { "date": "...", "git_commit": "...", "nlpl_version": "..." },
    "dispatch_speedup": 22.1,
    "benchmarks": {
        "fibonacci_iterative": {
            "nlpl_O0_ms": 0.85,
            "nlpl_O1_ms": 0.72,
            "nlpl_O2_ms": 0.68,
            "nlpl_O3_ms": 0.65,
            "c_o3_ms": 0.002,
            "nlpl_vs_c_ratio": 425.0
        },
        ...
    }
}
"""

import sys
import os
import time
import json
import statistics
import subprocess
import argparse
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root
PROJ_ROOT = Path(__file__).parent.parent
BENCH_DIR = PROJ_ROOT / "benchmarks"
SRC_DIR = PROJ_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------------------------
# Python-level NLPL interpreter timing (no subprocess overhead)
# ---------------------------------------------------------------------------

def time_nlpl_program(source_code: str, optimization_level: int = 0, runs: int = 5) -> Tuple[float, float]:
    """
    Time an NLPL program using the interpreter directly.

    Returns:
        (median_ms, stdev_ms) - execution times in milliseconds
    """
    from nlpl.interpreter.interpreter import Interpreter
    from nlpl.runtime.runtime import Runtime
    from nlpl.stdlib import register_stdlib
    from nlpl.parser.lexer import Lexer
    from nlpl.parser.parser import Parser

    # Pre-parse to separate parse time from execution time
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source=source_code)
    ast = parser.parse()

    times = []
    for _ in range(runs):
        rt = Runtime()
        register_stdlib(rt)
        interp = Interpreter(rt, source=source_code)
        t0 = time.perf_counter()
        interp.interpret(ast, optimization_level=optimization_level)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    med = statistics.median(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    return med, std


def time_nlpl_file(nlpl_path: str, optimization_level: int = 0, runs: int = 5) -> Tuple[float, float]:
    """Time an NLPL file."""
    with open(nlpl_path) as f:
        source = f.read()
    return time_nlpl_program(source, optimization_level=optimization_level, runs=runs)


# ---------------------------------------------------------------------------
# C benchmark compilation and timing
# ---------------------------------------------------------------------------

def compile_c(c_path: str, output_path: str, opt_level: str = "O3") -> bool:
    """Compile a C file. Returns True on success."""
    cmd = ["gcc", f"-{opt_level}", "-o", output_path, c_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  C compilation failed: {result.stderr.strip()}")
        return False
    return True


def time_c_binary(binary_path: str, runs: int = 20) -> Tuple[float, float]:
    """
    Time a compiled C binary.

    Extracts the time reported by the binary itself if it outputs
    'Time: X.XXXXXXXXX seconds', otherwise measures wall clock.

    Returns:
        (median_ms, stdev_ms)
    """
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        result = subprocess.run([binary_path], capture_output=True, text=True, timeout=10)
        t1 = time.perf_counter()

        # Try to extract printed time if available
        m = re.search(r"Time:\s*([\d.]+)\s*seconds", result.stdout)
        if m:
            times.append(float(m.group(1)) * 1000)
        else:
            times.append((t1 - t0) * 1000)

    med = statistics.median(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    return med, std


# ---------------------------------------------------------------------------
# Dispatch speedup measurement
# ---------------------------------------------------------------------------

def measure_dispatch_speedup() -> float:
    """Measure the speedup from the static dispatch table vs old regex approach."""
    import timeit
    import re as _re

    from nlpl.interpreter.interpreter import Interpreter
    from nlpl.runtime.runtime import Runtime
    from nlpl.stdlib import register_stdlib

    rt = Runtime()
    register_stdlib(rt)
    _ = Interpreter(rt)  # trigger table build
    table = Interpreter._DISPATCH_TABLE

    node_types = [
        "BinaryOperation", "VariableDeclaration", "IfStatement",
        "FunctionCall", "Literal", "Identifier", "WhileLoop", "ReturnStatement",
        "FunctionDefinition", "PrintStatement",
    ]

    def old_dispatch(nt):
        return "execute_" + _re.sub(r"(?<!^)(?=[A-Z])", "_", nt).lower()

    def new_dispatch(nt):
        return table.get(nt)

    n = 50000
    t_old = timeit.timeit(lambda: [old_dispatch(t) for t in node_types], number=n // len(node_types))
    t_new = timeit.timeit(lambda: [new_dispatch(t) for t in node_types], number=n // len(node_types))
    return t_old / t_new if t_new > 0 else 1.0


# ---------------------------------------------------------------------------
# Benchmark definitions
# ---------------------------------------------------------------------------

BENCHMARKS = [
    {
        "name": "fibonacci_iterative",
        "description": "Iterative Fibonacci(1000) - loop + integer arithmetic",
        "nlpl_file": str(BENCH_DIR / "bench_fibonacci.nlpl"),
        "c_file": str(BENCH_DIR / "bench_fibonacci_iter.c"),
        "c_opt": "O3",
    },
    {
        "name": "matrix_sum",
        "description": "Matrix sum (50x50) - nested loops, arithmetic",
        "nlpl_file": str(BENCH_DIR / "bench_matrix.nlpl"),
        "c_file": str(BENCH_DIR / "bench_matrix.c"),
        "c_opt": "O3",
    },
    {
        "name": "sieve_of_eratosthenes",
        "description": "Prime sieve up to 1000 - array access, conditional branching",
        "nlpl_file": str(BENCH_DIR / "bench_sieve.nlpl"),
        "c_file": str(BENCH_DIR / "bench_sieve.c"),
        "c_opt": "O3",
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_benchmark(bench: dict, runs: int, verbose: bool) -> dict:
    """Run a single benchmark and return results dict."""
    name = bench["name"]
    print(f"\n  [{name}] {bench['description']}")

    result = {
        "description": bench["description"],
        "nlpl_O0_ms": None,
        "nlpl_O1_ms": None,
        "nlpl_O2_ms": None,
        "nlpl_O3_ms": None,
        "c_o3_ms": None,
        "nlpl_vs_c_ratio": None,
        "nlpl_O3_vs_O0_speedup": None,
        "errors": [],
    }

    nlpl_file = bench.get("nlpl_file")
    c_file = bench.get("c_file")

    # Time NLPL at each optimization level
    if nlpl_file and Path(nlpl_file).exists():
        for opt in [0, 1, 2, 3]:
            key = f"nlpl_O{opt}_ms"
            try:
                med, std = time_nlpl_file(nlpl_file, optimization_level=opt, runs=runs)
                result[key] = round(med, 3)
                if verbose:
                    print(f"    NLPL -O{opt}: {med:.3f} ms  (stdev={std:.3f})")
            except Exception as e:
                result["errors"].append(f"nlpl O{opt}: {e}")
                if verbose:
                    print(f"    NLPL -O{opt}: ERROR - {e}")
    else:
        result["errors"].append(f"NLPL file not found: {nlpl_file}")
        print(f"    SKIP: NLPL file not found")

    # Time C reference at O3
    if c_file and Path(c_file).exists():
        with tempfile.NamedTemporaryFile(suffix="", delete=False) as f:
            c_out = f.name
        try:
            if compile_c(c_file, c_out, opt_level=bench.get("c_opt", "O3")):
                med, std = time_c_binary(c_out, runs=runs * 4)
                result["c_o3_ms"] = round(med, 6)
                if verbose:
                    print(f"    C -O3:    {med:.6f} ms  (stdev={std:.6f})")
            else:
                result["errors"].append("C compilation failed")
        except Exception as e:
            result["errors"].append(f"C benchmark: {e}")
            if verbose:
                print(f"    C -O3: ERROR - {e}")
        finally:
            try:
                os.unlink(c_out)
            except Exception:
                pass
    else:
        if verbose:
            print(f"    C reference: not available")

    # Compute ratios
    nlpl_best = result.get("nlpl_O3_ms") or result.get("nlpl_O2_ms") or result.get("nlpl_O0_ms")
    nlpl_o0 = result.get("nlpl_O0_ms")
    nlpl_o3 = result.get("nlpl_O3_ms")

    if nlpl_best and result["c_o3_ms"] and result["c_o3_ms"] > 0:
        result["nlpl_vs_c_ratio"] = round(nlpl_best / result["c_o3_ms"], 1)
        if verbose:
            print(f"    NLPL/C ratio: {result['nlpl_vs_c_ratio']}x slower")

    if nlpl_o0 and nlpl_o3 and nlpl_o0 > 0:
        result["nlpl_O3_vs_O0_speedup"] = round(nlpl_o0 / nlpl_o3, 3)
        if verbose:
            print(f"    O3 vs O0 speedup: {result['nlpl_O3_vs_O0_speedup']}x")

    return result


def get_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJ_ROOT), text=True
        ).strip()
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="NLPL Performance Baseline Runner")
    parser.add_argument("--output", default=str(PROJ_ROOT / "benchmarks" / "perf-baseline.json"),
                        help="Output JSON file (default: benchmarks/perf-baseline.json)")
    parser.add_argument("--runs", type=int, default=10,
                        help="Number of runs per measurement (default: 10)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print detailed timing for each benchmark")
    parser.add_argument("--skip-c", action="store_true",
                        help="Skip C compilation/benchmarks (faster)")
    args = parser.parse_args()

    print("NLPL Performance Baseline")
    print("=" * 50)
    print(f"Runs per measurement: {args.runs}")
    print(f"Output: {args.output}")

    # Measure dispatch speedup
    print("\nMeasuring dispatch table speedup...")
    dispatch_speedup = measure_dispatch_speedup()
    print(f"  Dispatch speedup: {dispatch_speedup:.1f}x (regex -> dict lookup)")

    # Run benchmarks
    bench_results = {}
    for bench in BENCHMARKS:
        # Honor --skip-c
        if args.skip_c:
            bench = dict(bench)
            bench["c_file"] = None
        bench_results[bench["name"]] = run_benchmark(bench, args.runs, args.verbose)

    # Build output
    from datetime import datetime
    output = {
        "meta": {
            "date": datetime.now().isoformat(),
            "git_commit": get_git_commit(),
            "runs_per_measurement": args.runs,
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "optimization_description": {
                "O0": "No AST optimization",
                "O1": "Basic: constant folding + DCE",
                "O2": "Standard: O1 + strength reduction + loop unrolling + inlining",
                "O3": "Aggressive: O2 + CSE + TCO + aggressive inlining",
            },
        },
        "dispatch_speedup_x": round(dispatch_speedup, 1),
        "baseline": bench_results,
    }

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Dispatch speedup: {dispatch_speedup:.1f}x")
    print()
    for bench_name, r in bench_results.items():
        print(f"{bench_name}:")
        o0 = r.get("nlpl_O0_ms")
        o3 = r.get("nlpl_O3_ms")
        c = r.get("c_o3_ms")
        ratio = r.get("nlpl_vs_c_ratio")
        speedup = r.get("nlpl_O3_vs_O0_speedup")
        if o0:
            print(f"  NLPL O0:        {o0:.3f} ms")
        if o3:
            print(f"  NLPL O3:        {o3:.3f} ms", end="")
            if speedup:
                print(f"  ({speedup:.2f}x vs O0)", end="")
            print()
        if c:
            print(f"  C -O3:          {c:.6f} ms")
        if ratio:
            print(f"  NLPL/C ratio:   {ratio}x slower than C")
        if r.get("errors"):
            for e in r["errors"]:
                print(f"  WARNING: {e}")
        print()

    print(f"Results saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
