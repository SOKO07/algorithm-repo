"""Reference shortest path length (A* on an inflated grid), used only as a yardstick.

Not one of the compared algorithms.  The grid is the same one the solvability
check uses (cell 0.5, obstacles inflated by ROBOT_RADIUS + MARGIN), moves are
8-connected.  The result approximates the continuous shortest path; the grid
makes it a little longer (octile metric) and the inflation (1.5 vs the real
collision limit 1.0) makes it a little more conservative, so a robot path can
be slightly SHORTER than this reference.
"""
import heapq
import math

from mapgen import GOAL, GRID, HEIGHT, MARGIN, ROBOT_RADIUS, START, WIDTH


def _blocked_grid(obstacles):
    n = int(WIDTH / GRID)
    inflate = ROBOT_RADIUS + MARGIN
    blocked = [[False] * n for _ in range(n)]
    for ox, oy, r in obstacles:
        rr = r + inflate
        i0, i1 = max(0, int((ox - rr) / GRID)), min(n - 1, int((ox + rr) / GRID))
        j0, j1 = max(0, int((oy - rr) / GRID)), min(n - 1, int((oy + rr) / GRID))
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                if math.dist(((i + .5) * GRID, (j + .5) * GRID), (ox, oy)) <= rr:
                    blocked[i][j] = True
    return blocked


def shortest_length(obstacles):
    """Length (world units) of the A* path from START to GOAL, or None."""
    n = int(WIDTH / GRID)
    blocked = _blocked_grid(obstacles)
    s = (int(START[0] / GRID), int(START[1] / GRID))
    g = (int(GOAL[0] / GRID), int(GOAL[1] / GRID))
    if blocked[s[0]][s[1]] or blocked[g[0]][g[1]]:
        return None

    def h(c):
        dx, dy = abs(c[0] - g[0]), abs(c[1] - g[1])
        return (max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)) * GRID

    steps = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
             (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
             (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))]
    best = {s: 0.0}
    heap = [(h(s), 0.0, s)]
    while heap:
        _, d, c = heapq.heappop(heap)
        if c == g:
            return d
        if d > best.get(c, math.inf):
            continue
        for di, dj, w in steps:
            a, b = c[0] + di, c[1] + dj
            if not (0 <= a < n and 0 <= b < n) or blocked[a][b]:
                continue
            if di and dj and (blocked[c[0] + di][c[1]] or blocked[c[0]][c[1] + dj]):
                continue  # no cutting corners between two blocked cells
            nd = d + w * GRID
            if nd < best.get((a, b), math.inf):
                best[(a, b)] = nd
                heapq.heappush(heap, (nd + h((a, b)), nd, (a, b)))
    return None
