"""Grid search of Bug2 parameters on the TUNING seeds only (0~49).

Usage (from personal_project/):  python src/tune_bug2.py

Score per setting: arrivals (higher is better), then collisions (lower).
Evaluation seeds (1000~) are never touched here.
"""
import itertools

import mapgen
import sim
from algo_bug2 import Bug2

HIT_DIST = (2.0, 3.0, 4.0)
FOLLOW_DIST = (1.0, 1.5, 2.5)
LEAVE_TOL = (0.5, 1.0, 2.0)

maps = []
for kind in mapgen.KINDS:
    ms, _ = mapgen.maps_for(kind, mapgen.TUNE_SEEDS)
    maps += ms
print(f"tuning maps: {len(maps)}")

rows = []
for hit, follow, tol in itertools.product(HIT_DIST, FOLLOW_DIST, LEAVE_TOL):
    out = {"arrived": 0, "collision": 0, "timeout": 0}
    by_kind = {k: 0 for k in mapgen.KINDS}
    for m in maps:
        res = sim.run(Bug2(hit, follow, tol), m)
        out[res.outcome] += 1
        if res.outcome == "arrived":
            by_kind[m.kind] += 1
    rows.append((hit, follow, tol, out, by_kind))
    print(f"hit={hit:3.1f} follow={follow:3.1f} tol={tol:3.1f} "
          f"arrived={out['arrived']:3d} collision={out['collision']:3d} "
          f"timeout={out['timeout']:3d} by_kind={by_kind}", flush=True)

best = max(rows, key=lambda r: (r[3]["arrived"], -r[3]["collision"]))
print(f"\nbest: hit={best[0]} follow={best[1]} tol={best[2]} {best[3]}")
