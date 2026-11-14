"""Sanity check: run the straight-line dummy on the evaluation seeds.

Usage (from personal_project/):  python src/check_straight.py
"""
from collections import Counter

import mapgen
import sim
from algo_straight import Straight

for kind in mapgen.KINDS:
    maps, rejected = mapgen.maps_for(kind, mapgen.EVAL_SEEDS)
    outcomes = Counter(sim.run(Straight(), m).outcome for m in maps)
    print(f"{kind:10s} maps={len(maps):3d} rejected={rejected:2d} "
          f"arrived={outcomes['arrived']:3d} collision={outcomes['collision']:3d} "
          f"timeout={outcomes['timeout']:3d}")
