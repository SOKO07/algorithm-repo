"""Grid search of APF parameters on the TUNING seeds only (0~49).

Usage (from personal_project/):  python src/tune_apf.py

Score per setting: arrivals (higher is better), then collisions (lower).
Evaluation seeds (1000~) are never touched here.
"""
import itertools

import mapgen
import sim
from algo_apf import APF

K_REP = (2.5, 5.0, 10.0, 20.0, 40.0, 80.0)
D0 = (4.0, 6.0, 8.0, 12.0)

maps = []
for kind in mapgen.KINDS:
    ms, _ = mapgen.maps_for(kind, mapgen.TUNE_SEEDS)
    maps += ms
print(f"tuning maps: {len(maps)}")

rows = []
for k_rep, d0 in itertools.product(K_REP, D0):
    out = {"arrived": 0, "collision": 0, "timeout": 0}
    by_kind = {k: 0 for k in mapgen.KINDS}
    for m in maps:
        res = sim.run(APF(k_rep, d0), m)
        out[res.outcome] += 1
        if res.outcome == "arrived":
            by_kind[m.kind] += 1
    rows.append((k_rep, d0, out, by_kind))
    print(f"k_rep={k_rep:6.1f} d0={d0:5.1f} arrived={out['arrived']:3d} "
          f"collision={out['collision']:3d} timeout={out['timeout']:3d} "
          f"by_kind={by_kind}", flush=True)

best = max(rows, key=lambda r: (r[2]["arrived"], -r[2]["collision"]))
print(f"\nbest: k_rep={best[0]} d0={best[1]} {best[2]}")
