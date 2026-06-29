import pytest
from carloforte._models import Island
from carloforte._serialiser import col_letter, range_str, serialise


def test_col_letter_single():
    assert col_letter(1) == "A"
    assert col_letter(26) == "Z"


def test_col_letter_double():
    assert col_letter(27) == "AA"
    assert col_letter(28) == "AB"


def test_range_str():
    island = Island(top_row=2, left_col=2, cells=[["Name", "Age"], ["Alice", 30]])
    assert range_str(island) == "B2:C3"


# --- CSV ---


def test_csv_contains_range_header():
    island = Island(top_row=1, left_col=1, cells=[["Name", "Age"], ["Alice", 30]])
    result = serialise("f.xlsx", {"S": [island]}, fmt="csv")
    assert "# S · A1:B2" in result


def test_csv_contains_data():
    island = Island(top_row=1, left_col=1, cells=[["Name", "Age"], ["Alice", 30]])
    result = serialise("f.xlsx", {"S": [island]}, fmt="csv")
    assert "Alice" in result
    assert "30" in result


# --- Markdown ---


def test_markdown_contains_sheet_header():
    island = Island(top_row=1, left_col=1, cells=[["Name", "Age"], ["Alice", 30]])
    result = serialise("f.xlsx", {"Sheet1": [island]}, fmt="markdown")
    assert "## Sheet: Sheet1" in result


def test_markdown_table_structure():
    island = Island(top_row=1, left_col=1, cells=[["Name", "Age"], ["Alice", 30]])
    result = serialise("f.xlsx", {"Sheet1": [island]}, fmt="markdown")
    assert "| Name | Age |" in result
    assert "| --- | --- |" in result
    assert "| Alice | 30 |" in result


def test_markdown_pipe_escaped():
    island = Island(top_row=1, left_col=1, cells=[["A|B"], ["val"]])
    result = serialise("f.xlsx", {"S": [island]}, fmt="markdown")
    assert "A\\|B" in result


# --- JSON ---


def test_json_contains_range():
    island = Island(top_row=1, left_col=1, cells=[["Name"], ["Alice"]])
    result = serialise("f.xlsx", {"S": [island]}, fmt="json")
    assert "A1:A2" in result


def test_json_contains_rows():
    island = Island(top_row=1, left_col=1, cells=[["Name"], ["Alice"]])
    result = serialise("f.xlsx", {"S": [island]}, fmt="json")
    assert "Alice" in result


# --- Invalid format ---


def test_invalid_format_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        serialise("f.xlsx", {}, fmt="xml")
