from carloforte._islands import find_islands, detect_header_row


def test_empty_grid():
    assert find_islands([]) == []


def test_single_cell():
    grid = [[None, None], [None, "hello"]]
    islands = find_islands(grid)
    assert len(islands) == 1
    assert islands[0].top_row == 2
    assert islands[0].left_col == 2
    assert islands[0].cells == [["hello"]]


def test_two_separate_islands():
    grid = [
        ["A", None, "X"],
        ["B", None, "Y"],
    ]
    islands = find_islands(grid)
    assert len(islands) == 2
    positions = {(i.top_row, i.left_col) for i in islands}
    assert (1, 1) in positions
    assert (1, 3) in positions


def test_contiguous_block():
    grid = [
        ["A", "B"],
        ["C", "D"],
    ]
    islands = find_islands(grid)
    assert len(islands) == 1
    assert islands[0].cells == [["A", "B"], ["C", "D"]]


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
    islands = find_islands(grid)
    assert len(islands) == 3


def test_detect_header_row_first_string_row():
    cells = [["Name", "Age", "City"], ["Alice", 30, "Rome"]]
    assert detect_header_row(cells) == 0


def test_detect_header_row_skips_numeric_first():
    cells = [[1, 2, 3], ["Name", "Age", "City"], ["Alice", 30, "Rome"]]
    assert detect_header_row(cells) == 1


def test_detect_header_row_fallback():
    cells = [[1, 2], [3, 4]]
    assert detect_header_row(cells) == 0
