# carloforte

[![CI](https://github.com/GioDecio/carloforte/actions/workflows/ci.yml/badge.svg)](https://github.com/GioDecio/carloforte/actions/workflows/ci.yml)

Extract structured data from Excel files with minimal token usage.

carloforte uses an island-detection algorithm to convert Excel sheets into a compact intermediate representation (CSV, Markdown, or JSON), making it efficient to pass spreadsheet data to LLMs.

## Installation
``uv add carloforte``

## Usage

```python
import carloforte

# Extract all sheets as CSV (default)
text = carloforte.extract("data.xlsx")

# Extract specific sheets as Markdown
text = carloforte.extract("data.xlsx", sheets=["Revenue", "Costs"], fmt="markdown")

# Extract as JSON
text = carloforte.extract("data.xlsx", fmt="json")
```

### Formats

| Format | Best for |
|--------|----------|
| `csv` | Compact, low token count |
| `markdown` | Readable, good for LLM prompts |
| `json` | Structured output, programmatic use |

### CLI

```bash
carloforte data.xlsx --fmt markdown
carloforte data.xlsx --sheets Revenue Costs --fmt json
```

## How it works

Excel sheets often contain multiple disconnected tables, empty rows, and metadata scattered around. carloforte detects each contiguous block of data ("island") independently and serialises only what matters — reducing token usage by 60–75% compared to passing raw Excel content to an LLM.

## Performance

Benchmarked against raw CSV export (worst case baseline). Run `examples/scripts/benchmark_tokens.py` to reproduce.

**Characters:**

| File | Raw CSV | Clean CSV | CSV islands | Markdown | JSON |
|------|--------:|----------:|------------:|---------:|-----:|
| `large_sparse` — 1 sheet, 5 islands spread over 165 rows | 4,470 | ↓ 1,480 (-67%) | ↓ 960 (-79%) | ↓ 1,453 (-68%) | ↓ 1,337 (-70%) |
| `fragmented` — 4 sheets, 4% fill, tiny tables far apart | 10,664 | ↓ 5,334 (-50%) | ↓ 4,811 (-55%) | ↓ 6,690 (-37%) | ↓ 6,221 (-42%) |
| `stray_cells` — 1 sheet, 7 islands + scattered stray cells | 2,143 | ↓ 1,668 (-22%) | ↓ 1,458 (-32%) | ↑ 2,175 (+2%) | ↓ 1,994 (-7%) |
| `multisheet` — 4 sheets, mixed structure | 1,304 | ↓ 1,084 (-17%) | ↓ 1,156 (-11%) | ↑ 1,879 (+44%) | ↑ 1,755 (+35%) |
| `invoice` — single invoice sheet | 4,180 | ↓ 3,745 (-10%) | ↓ 3,855 (-8%) | ↑ 5,097 (+22%) | ↑ 5,020 (+20%) |
| `minimal` — 1 sheet, 3 small islands | 248 | ↓ 216 (-13%) | ↓ 244 (-2%) | ↑ 417 (+68%) | ↑ 380 (+53%) |
| `enterprise` — 9 sheets, dense real-world complexity | 23,983 | ↓ 22,533 (-6%) | ↓ 22,639 (-6%) | ↑ 29,357 (+22%) | ↑ 28,741 (+20%) |

**Tokens** (cl100k_base):

| File | Raw CSV | Clean CSV | CSV islands | Markdown | JSON |
|------|--------:|----------:|------------:|---------:|-----:|
| `large_sparse` | 1,033 | ↓ 513 (-50%) | ↓ 443 (-57%) | ↓ 616 (-40%) | ↓ 605 (-41%) |
| `fragmented` | 2,556 | ↓ 1,504 (-41%) | ↓ 1,696 (-34%) | ↓ 2,375 (-7%) | ↓ 2,283 (-11%) |
| `stray_cells` | 630 | ↓ 555 (-12%) | ↓ 575 (-9%) | ↑ 824 (+31%) | ↑ 811 (+29%) |
| `multisheet` | 499 | ↓ 430 (-14%) | ↓ 484 (-3%) | ↑ 737 (+48%) | ↑ 721 (+45%) |
| `invoice` | 1,317 | ↓ 1,230 (-7%) | ↑ 1,323 (+0%) | ↑ 1,934 (+47%) | ↑ 1,839 (+40%) |
| `minimal` | 83 | ↓ 71 (-15%) | ↑ 89 (+7%) | ↑ 143 (+72%) | ↑ 139 (+67%) |
| `enterprise` | 9,606 | ↓ 9,311 (-3%) | ↑ 9,627 (+0%) | ↑ 11,723 (+22%) | ↑ 12,386 (+29%) |

## Architecture

```
carloforte/
├── __init__.py        public API: re-exports extract()
├── _extract.py        extract() — orchestrates the pipeline
├── _cli.py            main() — CLI entry point
├── _reader.py         load_workbook_sheets() — openpyxl → Grid
├── _islands.py        find_islands() — BFS island detection
└── _serialiser.py     serialise() — Grid → csv / markdown / json
```

```
carloforte.extract(path, sheets=None, fmt="csv")
│
│  1. _reader.load_workbook_sheets(path, sheets)
│     openpyxl → dict[sheet_name, Grid]
│
│  2. _islands.find_islands(grid)   ← per sheet
│     BFS over non-empty cells → list[Island]
│     each Island: bounding box + header row + data rows
│
│  3. _serialiser.serialise(sheet_islands, fmt)
│     "csv"      → one block per island, blank-line separated
│     "markdown" → ## heading per sheet, fenced table per island
│     "json"     → {"sheets": {"name": {"tables": [...]}}}
│
└─ returns str
```

## License

MIT
