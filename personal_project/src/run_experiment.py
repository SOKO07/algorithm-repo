"""Main experiment runner: every map x every algorithm, one run each.

Usage (from personal_project/):

    python src/run_experiment.py --set eval --out results/main.csv
    python src/run_experiment.py --set eval --out results/timing.csv --timing

--set     tune | eval   (required; eval = the 300-per-kind evaluation seeds,
                          run only after every parameter is frozen)
--limit N               use only the first N seeds per kind (smoke tests)
--timing                instead of the main run, time a fixed random subset
                        of maps (TIMING_MAPS) by running each algorithm
                        TIMING_REPEATS times and storing the median compute time

Resumable: rows are appended one at a time; rerunning the same command skips
what is already in the CSV.  Run it as ONE process, nothing else heavy running,
because compute time is a reported metric.

Map order and, per map, algorithm order are shuffled with a fixed seed so
warm-up or thermal effects do not favour one algorithm; the order is the same
on every run, so resuming stays consistent.
"""
import argparse
import csv
import os
import random
import statistics
import sys
import time

import mapgen
import reference
import sim
from algo_apf import APF
from algo_bug2 import Bug2
from algo_dwa import DWA

ALGOS = {"APF": APF, "Bug2": Bug2, "DWA": DWA}
SHUFFLE_SEED = 2026
TIMING_MAPS = 30
TIMING_REPEATS = 5
MAIN_FIELDS = ["set", "kind", "seed", "algo", "outcome", "distance", "steps",
               "compute_time", "astar_len", "n_obstacles"]
TIMING_FIELDS = ["set", "kind", "seed", "algo", "repeats", "median_compute_time"]


def seeds_for(which, limit):
    seeds = list(mapgen.TUNE_SEEDS if which == "tune" else mapgen.EVAL_SEEDS)
    return seeds[:limit] if limit else seeds


def read_done(path, fields):
    done = set()
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.add((row["kind"], int(row["seed"]), row["algo"]))
    return done


def open_writer(path, fields):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    new = not os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fields)
    if new:
        w.writeheader()
    return f, w


def ordered_maps(which, limit):
    """All (kind, seed) pairs in a fixed shuffled order."""
    pairs = [(k, s) for k in mapgen.KINDS for s in seeds_for(which, limit)]
    random.Random(SHUFFLE_SEED).shuffle(pairs)
    return pairs


def algo_order(kind, seed):
    names = list(ALGOS)
    random.Random(f"{SHUFFLE_SEED}:{kind}:{seed}").shuffle(names)
    return names


def run_main(args):
    done = read_done(args.out, MAIN_FIELDS)
    pairs = ordered_maps(args.set, args.limit)
    f, w = open_writer(args.out, MAIN_FIELDS)
    t0 = time.time()
    with f:
        for i, (kind, seed) in enumerate(pairs, 1):
            names = algo_order(kind, seed)
            if all((kind, seed, n) in done for n in names) or (kind, seed, "-") in done:
                continue
            m = mapgen.generate(kind, seed)
            if m is None:
                w.writerow({"set": args.set, "kind": kind, "seed": seed,
                            "algo": "-", "outcome": "rejected"})
                f.flush()
                continue
            ref = reference.shortest_length(m.obstacles)
            for name in names:
                if (kind, seed, name) in done:
                    continue
                res = sim.run(ALGOS[name](), m)
                w.writerow({"set": args.set, "kind": kind, "seed": seed,
                            "algo": name, "outcome": res.outcome,
                            "distance": f"{res.distance:.3f}", "steps": res.steps,
                            "compute_time": f"{res.compute_time:.6f}",
                            "astar_len": f"{ref:.3f}" if ref else "",
                            "n_obstacles": len(m.obstacles)})
                f.flush()
            el = time.time() - t0
            print(f"[{i}/{len(pairs)}] {kind} seed {seed}  elapsed {el:.0f}s",
                  flush=True)


def run_timing(args):
    pairs = ordered_maps(args.set, args.limit)
    maps = []
    for kind, seed in pairs:
        if mapgen.generate(kind, seed) is not None:
            maps.append((kind, seed))
    subset = random.Random(SHUFFLE_SEED + 1).sample(maps, min(TIMING_MAPS, len(maps)))
    done = read_done(args.out, TIMING_FIELDS)
    f, w = open_writer(args.out, TIMING_FIELDS)
    t0 = time.time()
    with f:
        for i, (kind, seed) in enumerate(subset, 1):
            m = mapgen.generate(kind, seed)
            for name in algo_order(kind, seed):
                if (kind, seed, name) in done:
                    continue
                times = [sim.run(ALGOS[name](), m).compute_time
                         for _ in range(TIMING_REPEATS)]
                w.writerow({"set": args.set, "kind": kind, "seed": seed,
                            "algo": name, "repeats": TIMING_REPEATS,
                            "median_compute_time":
                                f"{statistics.median(times):.6f}"})
                f.flush()
            print(f"[{i}/{len(subset)}] timing {kind} seed {seed}  "
                  f"elapsed {time.time() - t0:.0f}s", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--set", choices=("tune", "eval"), required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--timing", action="store_true")
    args = p.parse_args()
    (run_timing if args.timing else run_main)(args)


if __name__ == "__main__":
    sys.exit(main())
