"""Benchmark: Python vs Rust find_islands.

Usage:
    python examples/scripts/benchmark_islands.py
    python examples/scripts/benchmark_islands.py --profile
"""

import argparse
import cProfile
import pstats
import random
import statistics
import time

import _islands_rs
from carloforte._islands import find_islands as find_islands_py


def generate_grid(rows: int, cols: int, density: float, seed: int = 42) -> list[list]:
    rng = random.Random(seed)
    values = ["text", 1, 2.5, True]
    return [
        [rng.choice(values) if rng.random() < density else None for _ in range(cols)]
        for _ in range(rows)
    ]


def run_python(grid: list[list]) -> None:
    find_islands_py([row[:] for row in grid])


def run_rust(grid: list[list]) -> None:
    _islands_rs.find_islands([row[:] for row in grid])


def benchmark(label: str, fn, grid: list[list], n: int = 10) -> dict:
    times = []
    for _ in range(n):
        start = time.perf_counter()
        fn(grid)
        times.append((time.perf_counter() - start) * 1000)
    return {
        "label": label,
        "mean_ms": statistics.mean(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
    }


CONFIGS = [
    ("small", 100, 100),
    ("medium", 500, 500),
    ("large", 2000, 2000),
]

DENSITIES = [0.3, 0.7]


def run_benchmarks() -> None:
    header = f"{'Config':<25} {'Impl':<8} {'Mean (ms)':>10} {'Stdev (ms)':>12} {'Speedup':>9}"
    print(header)
    print("-" * len(header))

    for size_label, rows, cols in CONFIGS:
        for density in DENSITIES:
            grid = generate_grid(rows, cols, density)
            label = f"{size_label} {rows}x{cols} d={density}"

            py_result = benchmark(f"Python {label}", run_python, grid)
            rs_result = benchmark(f"Rust   {label}", run_rust, grid)
            speedup = (
                py_result["mean_ms"] / rs_result["mean_ms"]
                if rs_result["mean_ms"] > 0
                else float("inf")
            )

            print(
                f"{label:<25} {'python':<8} {py_result['mean_ms']:>10.2f} {py_result['stdev_ms']:>12.2f} {'':>9}"
            )
            print(
                f"{'':<25} {'rust':<8} {rs_result['mean_ms']:>10.2f} {rs_result['stdev_ms']:>12.2f} {speedup:>8.1f}x"
            )
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark Python vs Rust find_islands"
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Run cProfile and print top-20 cumulative stats",
    )
    args = parser.parse_args()

    if args.profile:
        pr = cProfile.Profile()
        pr.enable()
        run_benchmarks()
        pr.disable()
        stats = pstats.Stats(pr)
        stats.sort_stats("cumulative")
        stats.print_stats(20)
    else:
        run_benchmarks()


if __name__ == "__main__":
    main()
