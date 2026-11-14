"""Seeded random map generator with a solvability check (standard library only).

World: WIDTH x HEIGHT plane, circular obstacles, fixed start/goal.
A map is accepted only if start and goal are connected on a grid where
obstacles are inflated by ROBOT_RADIUS + MARGIN.
"""
import math
import random
from collections import deque
from dataclasses import dataclass

WIDTH = HEIGHT = 100.0
START = (5.0, 5.0)
GOAL = (95.0, 95.0)
ROBOT_RADIUS = 1.0
MARGIN = 0.5
GRID = 0.5  # cell size for the solvability check
KINDS = ("open", "cluttered", "corridor")

# Seed ranges keep tuning and evaluation maps disjoint.
TUNE_SEEDS = range(0, 50)
EVAL_SEEDS = range(1000, 1300)


@dataclass
class Map:
    kind: str
    seed: int
    obstacles: list  # [(x, y, r), ...]


def _clear_of_endpoints(x, y, r):
    pad = ROBOT_RADIUS + MARGIN + 3.0
    return (math.dist((x, y), START) > r + pad
            and math.dist((x, y), GOAL) > r + pad)


def _random_circles(rng, n, r_lo, r_hi):
    obs = []
    while len(obs) < n:
        r = rng.uniform(r_lo, r_hi)
        x, y = rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT)
        if _clear_of_endpoints(x, y, r):
            obs.append((x, y, r))
    return obs


def _corridor(rng, density=None, gap=None):
    """Vertical walls of touching circles, each with one gap of width `gap`."""
    obs = []
    gap = gap if gap is not None else rng.uniform(4.0, 8.0)
    r = 2.0
    for x in rng.sample(range(20, 81, 10), 3):
        gap_y = rng.uniform(15, 85)
        y = 0.0
        while y <= HEIGHT:
            if abs(y - gap_y) > gap / 2 + r:
                obs.append((float(x), y, r))
            y += r * 1.5
    return obs


def generate_raw(kind, seed, n_obstacles=None):
    rng = random.Random(f"{kind}:{seed}")
    if kind == "open":
        return _random_circles(rng, n_obstacles or 6, 4.0, 9.0)
    if kind == "cluttered":
        return _random_circles(rng, n_obstacles or 40, 2.0, 6.0)
    if kind == "corridor":
        return _corridor(rng)
    raise ValueError(kind)


def solvable(obstacles):
    """BFS (4-connected) on a grid with obstacles inflated by robot size."""
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
    s = (int(START[0] / GRID), int(START[1] / GRID))
    g = (int(GOAL[0] / GRID), int(GOAL[1] / GRID))
    if blocked[s[0]][s[1]] or blocked[g[0]][g[1]]:
        return False
    seen = {s}
    q = deque([s])
    while q:
        i, j = q.popleft()
        if (i, j) == g:
            return True
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < n and 0 <= b < n and not blocked[a][b] and (a, b) not in seen:
                seen.add((a, b))
                q.append((a, b))
    return False


def generate(kind, seed, n_obstacles=None):
    """Return a Map, or None if the seed yields an unsolvable map (rejected)."""
    obs = generate_raw(kind, seed, n_obstacles)
    return Map(kind, seed, obs) if solvable(obs) else None


def maps_for(kind, seeds):
    """Accepted maps for `seeds` plus the number rejected."""
    maps, rejected = [], 0
    for s in seeds:
        m = generate(kind, s)
        if m is None:
            rejected += 1
        else:
            maps.append(m)
    return maps, rejected


if __name__ == "__main__":
    for kind in KINDS:
        maps, rej = maps_for(kind, EVAL_SEEDS)
        avg = sum(len(m.obstacles) for m in maps) / max(1, len(maps))
        print(f"{kind:10s} accepted={len(maps):3d} rejected={rej:3d} "
              f"avg_obstacles={avg:.1f}")
