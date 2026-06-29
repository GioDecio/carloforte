# Rust Island Algorithm — Design Spec

**Date:** 2026-06-29
**Branch:** `feature/rust-islands`
**Status:** Approved

---

## Goal

Implement `find_islands` in Rust as a Python extension (via PyO3/maturin), benchmark it against the existing Python implementation, and — if performance gains are significant — integrate it into the library as an optional accelerator.

The work is split in two phases:
- **Phase A:** build the Rust extension and benchmark it against Python
- **Phase B:** integrate the Rust version into the library (decided after seeing benchmark results)

---

## Project Structure

```
carloforte-rs/          ← new Rust crate
  Cargo.toml
  src/
    lib.rs              ← find_islands exposed via PyO3
examples/scripts/
  benchmark_islands.py  ← benchmark + optional profiling entry point
```

The existing `src/carloforte/_islands.py` is untouched during Phase A.

---

## Rust Extension

**Crate:** `carloforte-rs`, compiled by maturin into a Python extension module named `_islands_rs`.

**Input:** `list[list[CellValue]]` where `CellValue = str | int | float | bool | None` — passed from Python as-is via PyO3.

**Output:** `list[dict]` with keys `top_row: int`, `left_col: int`, `cells: list[list[CellValue]]` — mirrors the Python `Island` dataclass fields exactly.

**Algorithm:** BFS connected-components, same logic as `_islands.py`:
1. Pad all rows to equal length
2. Iterate over cells; when a non-None unvisited cell is found, BFS to collect the connected component
3. Compute bounding box, extract sub-grid, emit island dict

PyO3 handles type conversion automatically. None maps to Python `None`, strings to `str`, numbers to `int`/`float`, booleans to `bool`.

---

## Benchmark Script

**File:** `examples/scripts/benchmark_islands.py`

**Grid sizes tested:**
| Size | Approx cells |
|------|-------------|
| Small | 100 × 100 |
| Medium | 500 × 500 |
| Large | 2000 × 2000 |

Each size is tested with two cell densities: 30% non-None and 70% non-None (affects BFS work).

**Per configuration:** 10 runs, report mean ± std deviation in milliseconds.

**Functions:**
- `generate_grid(rows, cols, density)` — synthetic grid generator
- `run_python(grid)` — calls `_islands.find_islands`
- `run_rust(grid)` — calls `_islands_rs.find_islands`
- `benchmark(label, fn, grid, n=10)` — times n runs, returns stats
- `main()` — iterates over all configs, prints results table

**Profiling support:**
- VS Code built-in Python profiler works out of the box: open the script and use "Run with Python Profiler" — the clean function structure (`run_python`, `run_rust`) makes the flamegraph readable.
- CLI flag `--profile` runs `cProfile` programmatically and prints a top-20 cumulative stats table.

---

## Build & Run

```bash
# Install maturin (dev dependency)
pip install maturin

# Build the Rust extension in place
cd carloforte-rs && maturin develop --release

# Run benchmark
python examples/scripts/benchmark_islands.py

# Run with CLI profiler
python examples/scripts/benchmark_islands.py --profile
```

---

## Phase B (post-benchmark)

If Rust is meaningfully faster (target: >5× on medium grids), integrate as optional accelerator:

```python
# src/carloforte/_islands.py
try:
    from _islands_rs import find_islands
except ImportError:
    # pure Python fallback
    def find_islands(grid): ...
```

This keeps the library installable without Rust. Users who install the compiled wheel get the fast path automatically.

---

## Out of Scope

- Rust implementation of `_reader.py` or `_serialiser.py`
- Async or parallel BFS within Rust
- Windows cross-compilation (handled later if needed)
