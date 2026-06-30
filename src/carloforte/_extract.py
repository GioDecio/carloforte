from loguru import logger

from ._islands import find_islands
from ._reader import load_workbook_sheets
from ._serialiser import serialise

_FORMATS = ("csv", "markdown", "json")


def extract(
    path: str,
    sheets: list[str] | None = None,
    fmt: str = "csv",
) -> str:
    if fmt not in _FORMATS:
        raise ValueError(f"Unknown format {fmt!r}. Choose: {_FORMATS}")
    logger.debug(
        "Loading {path}, sheets={sheets}, fmt={fmt}", path=path, sheets=sheets, fmt=fmt
    )
    grids = load_workbook_sheets(path, sheets)
    logger.debug("Loaded {n} sheet(s)", n=len(grids))
    sheet_islands = {name: find_islands(grid) for name, grid in grids.items()}
    logger.debug(
        "Found islands: { {name: len(isl)} for name, isl in sheet_islands.items() }"
    )
    return serialise(path, sheet_islands, fmt)
