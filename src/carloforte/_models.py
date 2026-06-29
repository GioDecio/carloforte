from dataclasses import dataclass

CellValue = str | int | float | bool | None


@dataclass
class Island:
    top_row: int  # 1-indexed (Excel convention)
    left_col: int  # 1-indexed
    cells: list[list[CellValue]]

    @property
    def height(self) -> int:
        return len(self.cells)

    @property
    def width(self) -> int:
        return len(self.cells[0]) if self.cells else 0
