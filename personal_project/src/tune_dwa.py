"""Grid search of DWA parameters on the TUNING seeds only (0~49).

Usage (from personal_project/):  python src/tune_dwa.py

DWA is slow (each step rolls out dozens of trajectories), so settings run in
a few parallel worker processes (WORKERS).  Score per setting: arrivals (higher is better),
then collisions (lower).  Evaluation seeds (1000~) are never touched here.
"""
import itertools
import os
from multiprocessing import Pool

import mapgen
import sim
from algo_dwa import DWA

BETA = (0.6, 1.0)
GAMMA = (1.0, 2.0)
T_PRED = (1.5, 2.0, 3.0)
WORKERS = 4  # keep the machine usable; raise only if you do not mind the fans


def run_one(args):
    beta, gamma, t_pred, kind, seed = args
    m = mapgen.generate(kind, seed)
    if m is None:
        return (beta, gamma, t_pred, kind, None)
    return (beta, gamma, t_pred, kind, sim.run(DWA(beta, gamma, t_pred), m).outcome)


if __name__ == "__main__":
    settings = list(itertools.product(BETA, GAMMA, T_PRED))
    jobs = [(b, g, t, k, s) for (b, g, t) in settings
            for k in mapgen.KINDS for s in mapgen.TUNE_SEEDS]
    print(f"settings={len(settings)} runs={len(jobs)} workers={WORKERS}",
          flush=True)
    with Pool(WORKERS) as pool:
        results = pool.map(run_one, jobs, chunksize=8)

    rows = []
    for (b, g, t) in settings:
        out = {"arrived": 0, "collision": 0, "timeout": 0}
        by_kind = {k: 0 for k in mapgen.KINDS}
        for rb, rg, rt, kind, outcome in results:
            if (rb, rg, rt) == (b, g, t) and outcome is not None:
                out[outcome] += 1
                if outcome == "arrived":
                    by_kind[kind] += 1
        rows.append((b, g, t, out, by_kind))
        print(f"beta={b:3.1f} gamma={g:3.1f} t_pred={t:3.1f} "
              f"arrived={out['arrived']:3d} collision={out['collision']:3d} "
              f"timeout={out['timeout']:3d} by_kind={by_kind}")

    best = max(rows, key=lambda r: (r[3]["arrived"], -r[3]["collision"]))
    print(f"\nbest: beta={best[0]} gamma={best[1]} t_pred={best[2]} {best[3]}")
