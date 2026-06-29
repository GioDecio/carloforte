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

| File | Raw CSV | CSV islands | Markdown | JSON |
|------|--------:|------------:|---------:|-----:|
| `large_sparse` — 1 sheet, 5 islands spread over 165 rows | 4,470 | ↓ 960 | ↓ 1,453 | ↓ 1,337 |
| `fragmented` — 4 sheets, 4% fill, tiny tables far apart | 10,664 | ↓ 4,811 | ↓ 6,690 | ↓ 6,221 |
| `stray_cells` — 1 sheet, 7 islands + scattered stray cells | 2,143 | ↓ 1,458 | ↑ 2,175 | ↓ 1,994 |
| `multisheet` — 4 sheets, mixed structure | 1,304 | ↓ 1,156 | ↑ 1,879 | ↑ 1,755 |
| `minimal` — 1 sheet, 3 small islands | 248 | ↓ 244 | ↑ 417 | ↑ 380 |
| `enterprise` — 9 sheets, dense real-world complexity | 23,983 | ↓ 22,639 | ↑ 29,357 | ↑ 28,741 |

**Tokens** (cl100k_base):

| File | Raw CSV | CSV islands | Markdown | JSON |
|------|--------:|------------:|---------:|-----:|
| `large_sparse` | 1,033 | ↓ 443 | ↓ 616 | ↓ 605 |
| `fragmented` | 2,556 | ↓ 1,696 | ↓ 2,375 | ↓ 2,283 |
| `stray_cells` | 630 | ↓ 575 | ↑ 824 | ↑ 811 |
| `multisheet` | 499 | ↓ 484 | ↑ 737 | ↑ 721 |
| `minimal` | 83 | ↑ 89 | ↑ 143 | ↑ 139 |
| `enterprise` | 9,606 | ↑ 9,627 | ↑ 11,723 | ↑ 12,386 |

## Architecture

```
extract("file.xlsx", fmt="csv")
│
├─ _reader        load_workbook_sheets()
│                 openpyxl → dict[sheet_name, Grid]
│
├─ _islands       find_islands(grid)
│                 BFS over non-empty cells → list[Island]
│                 each Island has a bounding box + header row + data rows
│
└─ _serialiser    serialise(sheet_islands, fmt)
                  csv      →  one block per island, separated by blank lines
                  markdown →  one ## heading per sheet, fenced tables per island
                  json     →  { sheets: { name: { tables: [...] } } }
```

## License

MIT
