from carloforte._models import Island


def test_island_height_width():
    cells = [["A", "B"], ["C", "D"], ["E", "F"]]
    island = Island(top_row=1, left_col=1, cells=cells)
    assert island.height == 3
    assert island.width == 2


def test_island_single_cell():
    island = Island(top_row=5, left_col=3, cells=[["hello"]])
    assert island.height == 1
    assert island.width == 1


def test_island_empty_cells():
    island = Island(top_row=1, left_col=1, cells=[])
    assert island.height == 0
    assert island.width == 0
