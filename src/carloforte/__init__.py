import argparse
from loguru import logger
from ._reader import load_workbook_sheets
from ._islands import find_islands
from ._serialiser import serialise

logger.disable("carloforte")

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


def main() -> None:
    logger.enable("carloforte")
    parser = argparse.ArgumentParser(prog="carloforte")
    parser.add_argument("file", help="Path to the Excel file")
    parser.add_argument("--sheets", nargs="+", help="Sheet names to process")
    parser.add_argument("--fmt", default="csv", choices=_FORMATS, help="Output format")
    args = parser.parse_args()
    print(extract(args.file, sheets=args.sheets, fmt=args.fmt))


__all__ = ["extract"]
