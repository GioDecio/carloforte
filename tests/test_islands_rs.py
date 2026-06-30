import pytest

_islands_rs = pytest.importorskip("_islands_rs")

from carloforte._islands import find_islands as py_find_islands  # noqa: E402


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
