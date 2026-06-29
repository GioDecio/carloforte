# Rust Island Algorithm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `find_islands` in Rust as a PyO3 extension, verify correctness parity with Python via pytest, and benchmark both versions across synthetic grids of varying sizes.

**Architecture:** A new Rust crate (`carloforte-rs/`) compiled by maturin into `_islands_rs`, a Python extension module. The Python `_islands.py` is untouched. Tests in `tests/test_islands_rs.py` assert output parity between the two implementations. A benchmark script `examples/scripts/benchmark_islands.py` times both across small/medium/large grids.

**Tech Stack:** Rust 1.90, PyO3 0.22, maturin, pytest 8+, Python 3.14

## Global Constraints

- Python ≥ 3.14
- Rust edition 2021
- PyO3 version 0.22
- Do not modify `src/carloforte/_islands.py`
- The Rust function returns `list[dict]` with keys `top_row: int`, `left_col: int`, `cells: list[list]`
- Tests skip gracefully if `_islands_rs` is not compiled (`pytest.importorskip`)
- Branch: `feature/rust-islands`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `carloforte-rs/Cargo.toml` | Create | Crate manifest, PyO3 dependency |
| `carloforte-rs/src/lib.rs` | Create | `find_islands` in Rust, exposed via PyO3 |
| `tests/test_islands_rs.py` | Create | Correctness parity tests |
| `examples/scripts/benchmark_islands.py` | Create | Benchmark + CLI profiling |
| `pyproject.toml` | Modify | Add `maturin` to dev dependencies |

---

## Task 1: Rust crate scaffold with stub

**Files:**
- Create: `carloforte-rs/Cargo.toml`
- Create: `carloforte-rs/src/lib.rs`
- Modify: `pyproject.toml` (add maturin to dev deps)

**Interfaces:**
- Produces: `_islands_rs.find_islands(grid)` — importable from Python, returns `[]` (stub)

- [ ] **Step 1: Add maturin to dev dependencies**

In `pyproject.toml`, add `maturin>=1.7` to `[dependency-groups] dev`:

```toml
[dependency-groups]
dev = [
    "commitizen>=4.16.4",
    "maturin>=1.7",
    "mypy>=1.16",
    "openpyxl-stubs",
    "pre-commit>=4.0",
    "pytest>=8.0",
    "ruff>=0.15.20",
    "tiktoken>=0.13.0",
]
```

- [ ] **Step 2: Install maturin**

```bash
uv pip install maturin
```

Expected: maturin installed in `.venv`.

- [ ] **Step 3: Create Cargo.toml**

```toml
[package]
name = "carloforte-rs"
version = "0.1.0"
edition = "2021"

[lib]
name = "_islands_rs"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22", features = ["extension-module"] }
```

Save to `carloforte-rs/Cargo.toml`.

- [ ] **Step 4: Create stub lib.rs**

```rust
use pyo3::prelude::*;

#[pyfunction]
fn find_islands(_py: Python, _grid: Vec<Vec<Option<PyObject>>>) -> PyResult<Vec<PyObject>> {
    Ok(vec![])
}

#[pymodule]
fn _islands_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_islands, m)?)?;
    Ok(())
}
```

Save to `carloforte-rs/src/lib.rs`.

- [ ] **Step 5: Build and verify the stub is importable**

```bash
cd carloforte-rs && maturin develop --release && cd ..
python -c "import _islands_rs; print(_islands_rs.find_islands([[1, None], [None, 2]]))"
```

Expected output: `[]`

- [ ] **Step 6: Commit**

```bash
git add carloforte-rs/ pyproject.toml
git commit -m "feat(rust): scaffold PyO3 crate with stub find_islands"
```

---

## Task 2: Correctness parity tests (failing)

**Files:**
- Create: `tests/test_islands_rs.py`

**Interfaces:**
- Consumes: `_islands_rs.find_islands(grid: list[list]) -> list[dict]` where each dict has `top_row: int`, `left_col: int`, `cells: list[list]`
- Consumes: `carloforte._islands.find_islands(grid) -> list[Island]` where `Island` has `.top_row`, `.left_col`, `.cells`

- [ ] **Step 1: Write the test file**

```python
import pytest

_islands_rs = pytest.importorskip("_islands_rs")

from carloforte._islands import find_islands as py_find_islands


def _py_to_dicts(islands):
    return [
        {"top_row": i.top_row, "left_col": i.left_col, "cells": i.cells}
        for i in islands
    ]


def _assert_parity(grid):
    expected = _py_to_dicts(py_find_islands([row[:] for row in grid]))
    actual = _islands_rs.find_islands([row[:] for row in grid])
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert a["top_row"] == e["top_row"]
        assert a["left_col"] == e["left_col"]
        assert a["cells"] == e["cells"]


def test_empty_grid():
    assert _islands_rs.find_islands([]) == []


def test_single_cell():
    _assert_parity([[None, None], [None, "hello"]])


def test_two_separate_islands():
    _assert_parity([["A", None, "X"], ["B", None, "Y"]])


def test_contiguous_block():
    _assert_parity([["A", "B"], ["C", "D"]])


def test_scattered_islands():
    grid = [
        [None, None, None, None, None, None],
        [None, "Name", "Dept", None, None, None],
        [None, "Alice", "Eng", None, None, None],
        [None, "Bob", "Mkt", None, None, None],
        [None, None, None, None, None, None],
        ["Q1", "Q2", "Q3", None, None, None],
        [10, 20, 30, None, None, None],
        [None, None, None, "Proj", "Owner", "Status"],
        [None, None, None, "Alpha", "Alice", "Active"],
    ]
    _assert_parity(grid)


def test_mixed_types():
    _assert_parity([[1, "hello", True, 3.14], [None, None, None, None]])
```

Save to `tests/test_islands_rs.py`.

- [ ] **Step 2: Run tests and confirm they fail (not skip)**

```bash
pytest tests/test_islands_rs.py -v
```

Expected: `test_empty_grid` PASSES (stub returns `[]`), all others FAIL because stub always returns `[]`.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/test_islands_rs.py
git commit -m "test(rust): add correctness parity tests for _islands_rs"
```

---

## Task 3: Implement find_islands in Rust

**Files:**
- Modify: `carloforte-rs/src/lib.rs`

**Interfaces:**
- Consumes: `grid: Vec<Vec<Option<PyObject>>>` — None means empty cell
- Produces: `Vec<PyObject>` — each element is a Python dict `{top_row, left_col, cells}`

- [ ] **Step 1: Replace stub with full implementation**

```rust
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::VecDeque;

#[pyfunction]
fn find_islands(py: Python, grid: Vec<Vec<Option<PyObject>>>) -> PyResult<Vec<PyObject>> {
    if grid.is_empty() {
        return Ok(vec![]);
    }

    let max_row = grid.len();
    let max_col = grid.iter().map(|r| r.len()).max().unwrap_or(0);

    // Pad rows to equal width
    let padded: Vec<Vec<Option<&PyObject>>> = grid
        .iter()
        .map(|row| {
            let mut r: Vec<Option<&PyObject>> = row.iter().map(|c| c.as_ref()).collect();
            r.resize(max_col, None);
            r
        })
        .collect();

    let mut visited = vec![vec![false; max_col]; max_row];
    let mut islands: Vec<PyObject> = Vec::new();

    for start_r in 0..max_row {
        for start_c in 0..max_col {
            if visited[start_r][start_c] || padded[start_r][start_c].is_none() {
                visited[start_r][start_c] = true;
                continue;
            }

            let mut component: Vec<(usize, usize)> = Vec::new();
            let mut queue: VecDeque<(usize, usize)> = VecDeque::new();
            queue.push_back((start_r, start_c));
            visited[start_r][start_c] = true;

            while let Some((r, c)) = queue.pop_front() {
                component.push((r, c));
                for (dr, dc) in [(-1i64, 0i64), (1, 0), (0, -1), (0, 1)] {
                    let nr = r as i64 + dr;
                    let nc = c as i64 + dc;
                    if nr >= 0
                        && (nr as usize) < max_row
                        && nc >= 0
                        && (nc as usize) < max_col
                    {
                        let nr = nr as usize;
                        let nc = nc as usize;
                        if !visited[nr][nc] && padded[nr][nc].is_some() {
                            visited[nr][nc] = true;
                            queue.push_back((nr, nc));
                        }
                    }
                }
            }

            let min_r = component.iter().map(|(r, _)| *r).min().unwrap();
            let max_r = component.iter().map(|(r, _)| *r).max().unwrap();
            let min_c = component.iter().map(|(_, c)| *c).min().unwrap();
            let max_c = component.iter().map(|(_, c)| *c).max().unwrap();

            let cells = PyList::new(
                py,
                (min_r..=max_r).map(|r| {
                    PyList::new(
                        py,
                        (min_c..=max_c).map(|c| match padded[r][c] {
                            Some(v) => v.clone_ref(py).into_pyobject(py).unwrap().unbind(),
                            None => py.None(),
                        }),
                    )
                    .unwrap()
                }),
            )
            .unwrap();

            let island = PyDict::new(py);
            island.set_item("top_row", min_r + 1)?;
            island.set_item("left_col", min_c + 1)?;
            island.set_item("cells", cells)?;
            islands.push(island.unbind().into());
        }
    }

    Ok(islands)
}

#[pymodule]
fn _islands_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_islands, m)?)?;
    Ok(())
}
```

Save to `carloforte-rs/src/lib.rs`.

- [ ] **Step 2: Rebuild**

```bash
cd carloforte-rs && maturin develop --release && cd ..
```

Expected: compiles without errors.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_islands_rs.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 4: Run full test suite to check no regressions**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add carloforte-rs/src/lib.rs
git commit -m "feat(rust): implement find_islands BFS in Rust via PyO3"
```

---

## Task 4: Benchmark script with profiling support

**Files:**
- Create: `examples/scripts/benchmark_islands.py`

**Interfaces:**
- Consumes: `_islands_rs.find_islands(grid)` and `carloforte._islands.find_islands(grid)`

- [ ] **Step 1: Write the benchmark script**

```python
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
            speedup = py_result["mean_ms"] / rs_result["mean_ms"] if rs_result["mean_ms"] > 0 else float("inf")

            print(
                f"{label:<25} {'python':<8} {py_result['mean_ms']:>10.2f} {py_result['stdev_ms']:>12.2f} {'':>9}"
            )
            print(
                f"{'':<25} {'rust':<8} {rs_result['mean_ms']:>10.2f} {rs_result['stdev_ms']:>12.2f} {speedup:>8.1f}x"
            )
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Python vs Rust find_islands")
    parser.add_argument("--profile", action="store_true", help="Run cProfile and print top-20 cumulative stats")
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
```

Save to `examples/scripts/benchmark_islands.py`.

- [ ] **Step 2: Run the benchmark to verify it works**

```bash
python examples/scripts/benchmark_islands.py
```

Expected: prints a table with mean/stdev/speedup for each config. No errors.

- [ ] **Step 3: Run with --profile to verify profiling works**

```bash
python examples/scripts/benchmark_islands.py --profile
```

Expected: benchmark table followed by cProfile top-20 cumulative stats.

- [ ] **Step 4: Commit**

```bash
git add examples/scripts/benchmark_islands.py
git commit -m "feat(bench): add Python vs Rust benchmark script with --profile flag"
```
