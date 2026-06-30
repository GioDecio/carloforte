import argparse

from loguru import logger

from ._extract import _FORMATS, extract


def main() -> None:
    logger.enable("carloforte")
    parser = argparse.ArgumentParser(prog="carloforte")
    parser.add_argument("file", help="Path to the Excel file")
    parser.add_argument("--sheets", nargs="+", help="Sheet names to process")
    parser.add_argument("--fmt", default="csv", choices=_FORMATS, help="Output format")
    args = parser.parse_args()
    print(extract(args.file, sheets=args.sheets, fmt=args.fmt))
