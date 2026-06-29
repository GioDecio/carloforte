import csv
import io
import json
import re
from ._models import Island, CellValue
from ._islands import detect_header_row

CellGrid = list[list[CellValue]]


def col_letter(n: int) -> str:
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def range_str(island: Island) -> str:
    top_left = f"{col_letter(island.left_col)}{island.top_row}"
    bottom_right = f"{col_letter(island.left_col + island.width - 1)}{island.top_row + island.height - 1}"
    return f"{top_left}:{bottom_right}"


def _cell(v: CellValue) -> str:
    return "" if v is None else str(v)


def _safe_id(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", name)


def _to_csv(sheet_islands: dict[str, list[Island]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    for sheet_name, islands in sheet_islands.items():
        for island in islands:
            buf.write(f"# {sheet_name} · {range_str(island)}\n")
            for row in island.cells:
                writer.writerow([_cell(v) for v in row])
            buf.write("\n")
    return buf.getvalue()


def _to_markdown(path: str, sheet_islands: dict[str, list[Island]]) -> str:
    def md_cell(v: CellValue) -> str:
        return _cell(v).replace("|", "\\|")

    filename = __import__("pathlib").Path(path).name
    sections = [f"# {filename}\n"]
    for sheet_name, islands in sheet_islands.items():
        sections.append(f"## Sheet: {sheet_name}\n")
        if not islands:
            sections.append("_No data islands found._\n")
            continue
        for idx, island in enumerate(islands):
            table_id = f"{_safe_id(sheet_name)}_t{idx}"
            header_idx = detect_header_row(island.cells)
            headers = [md_cell(v) for v in island.cells[header_idx]]
            # rows before the header (pre-header data) + rows after
            pre_header = island.cells[:header_idx]
            rows = pre_header + island.cells[header_idx + 1 :]
            sections.append(f"### {table_id} · {range_str(island)}")
            sections.append("| " + " | ".join(headers) + " |")
            sections.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in rows:
                padded = list(row) + [None] * (len(headers) - len(row))
                sections.append("| " + " | ".join(md_cell(v) for v in padded) + " |")
            sections.append("")
    return "\n".join(sections)


def _to_json(sheet_islands: dict[str, list[Island]]) -> str:
    result = {}
    for sheet_name, islands in sheet_islands.items():
        result[sheet_name] = [{"range": range_str(i), "rows": i.cells} for i in islands]
    return json.dumps(result, default=str)


def serialise(
    path: str,
    sheet_islands: dict[str, list[Island]],
    fmt: str,
) -> str:
    if fmt == "csv":
        return _to_csv(sheet_islands)
    if fmt == "markdown":
        return _to_markdown(path, sheet_islands)
    if fmt == "json":
        return _to_json(sheet_islands)
    raise ValueError(f"Unknown format {fmt!r}. Choose: 'csv', 'markdown', 'json'")
