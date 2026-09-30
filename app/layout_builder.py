"""Arrange panels into comic pages (rows of panels)."""

# Rows per page pattern, by number of panels on that page
PATTERNS = {
    1: [[0]],
    2: [[0], [1]],
    3: [[0], [1, 2]],
    4: [[0, 1], [2, 3]],
    5: [[0], [1, 2], [3, 4]],
    6: [[0, 1], [2, 3], [4, 5]],
}
PANELS_PER_PAGE = 6


def build_layout(panels: list[dict]) -> list[dict]:
    pages = []
    for start in range(0, len(panels), PANELS_PER_PAGE):
        chunk = panels[start:start + PANELS_PER_PAGE]
        rows = [[chunk[i] for i in row] for row in PATTERNS[len(chunk)]]
        pages.append({"number": len(pages) + 1, "rows": rows})
    return pages
