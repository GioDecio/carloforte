from collections import deque
from ._models import Island, CellValue

CellGrid = list[list[CellValue]]


def detect_header_row(cells: list[list[CellValue]]) -> int:
    for i, row in enumerate(cells):
        non_null = [v for v in row if v is not None]
        if non_null and all(isinstance(v, str) for v in non_null):
            return i
    return 0


def find_islands(grid: CellGrid) -> list[Island]:
    if not grid:
        return []

    max_row = len(grid)
    max_col = max((len(row) for row in grid), default=0)

    for row in grid:
        while len(row) < max_col:
            row.append(None)

    visited = [[False] * max_col for _ in range(max_row)]
    islands: list[Island] = []

    for start_r in range(max_row):
        for start_c in range(max_col):
            if visited[start_r][start_c] or grid[start_r][start_c] is None:
                visited[start_r][start_c] = True
                continue

            component: set[tuple[int, int]] = set()
            queue: deque[tuple[int, int]] = deque()
            queue.append((start_r, start_c))
            visited[start_r][start_c] = True

            while queue:
                r, c = queue.popleft()
                component.add((r, c))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < max_row
                        and 0 <= nc < max_col
                        and not visited[nr][nc]
                        and grid[nr][nc] is not None
                    ):
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            min_r = min(r for r, _ in component)
            max_r = max(r for r, _ in component)
            min_c = min(c for _, c in component)
            max_c = max(c for _, c in component)

            islands.append(
                Island(
                    top_row=min_r + 1,
                    left_col=min_c + 1,
                    cells=[
                        [grid[r][c] for c in range(min_c, max_c + 1)]
                        for r in range(min_r, max_r + 1)
                    ],
                )
            )

    return islands
