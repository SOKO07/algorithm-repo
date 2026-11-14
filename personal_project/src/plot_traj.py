"""Draw representative trajectories (needs matplotlib; the simulation does not).

Usage (from personal_project/):  python src/plot_traj.py

Writes PNG files to figures/:
  fig_wall.png               APF vs Bug2 vs DWA on one long wall across the path
  fig_traj_<kind>.png        the three algorithms on one TUNING-seed map per kind

Only tuning seeds and a hand-made wall are used, so no evaluation map is looked
at before the main experiment.
"""
import math
import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
except ImportError:
    sys.exit("matplotlib is required for plotting: pip install matplotlib")

import mapgen
import sim
from algo_apf import APF
from algo_bug2 import Bug2
from algo_dwa import DWA

OUT = os.path.join(os.path.dirname(__file__), "..", "figures")
ALGOS = (("APF", APF), ("Bug2", Bug2), ("DWA", DWA))
COLORS = {"APF": "#d95f02", "Bug2": "#1b9e77", "DWA": "#7570b3"}
TUNE_SEED = {"open": 3, "cluttered": 3, "corridor": 3}  # tuning seeds only


def wall_map(half=20, step=3, r=2.0):
    """Wall perpendicular to the start-goal line, centered at (50, 50)."""
    s = 2 ** -0.5
    obs = [(50.0 + s * t, 50.0 - s * t, r) for t in range(-half, half + 1, step)]
    return mapgen.Map("wall", -1, obs)


def draw_map(ax, game_map):
    ax.add_patch(Rectangle((0, 0), mapgen.WIDTH, mapgen.HEIGHT, fill=False,
                           edgecolor="black", linewidth=1.2))
    for x, y, r in game_map.obstacles:
        ax.add_patch(Circle((x, y), r, color="#999999", zorder=1))
    ax.plot(*mapgen.START, marker="s", color="black", markersize=7, zorder=4)
    ax.plot(*mapgen.GOAL, marker="*", color="gold", markeredgecolor="black",
            markersize=14, zorder=4)
    ax.set_xlim(-2, mapgen.WIDTH + 2)
    ax.set_ylim(-2, mapgen.HEIGHT + 2)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def draw_run(ax, name, result, label=None):
    xs, ys = zip(*result.path)
    ax.plot(xs, ys, color=COLORS[name], linewidth=1.6, zorder=3,
            label=label or name)
    marker = {"arrived": "o", "collision": "X", "timeout": "P"}[result.outcome]
    ax.plot(xs[-1], ys[-1], marker=marker, color=COLORS[name],
            markeredgecolor="black", markersize=9, zorder=5)


def describe(result):
    return f"{result.outcome}, dist {result.distance:.0f}, steps {result.steps}"


def run_all(game_map):
    return {name: sim.run(cls(), game_map) for name, cls in ALGOS}


def fig_wall():
    m = wall_map()
    results = run_all(m)
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    draw_map(ax, m)
    for name, res in results.items():
        draw_run(ax, name, res, f"{name}: {describe(res)}")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.set_title("Long wall across the straight path\n"
                 "(marker at the end: o arrived, P timeout, X collision)",
                 fontsize=10)
    return fig, results


def fig_kind(kind):
    m = mapgen.generate(kind, TUNE_SEED[kind])
    if m is None:
        raise SystemExit(f"{kind} seed {TUNE_SEED[kind]} was rejected as unsolvable")
    results = run_all(m)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, (name, _) in zip(axes, ALGOS):
        draw_map(ax, m)
        draw_run(ax, name, results[name])
        ax.set_title(f"{name}\n{describe(results[name])}", fontsize=9)
    fig.suptitle(f"{kind} map, tuning seed {m.seed}", fontsize=11)
    return fig, results


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [("fig_wall.png", fig_wall)]
    jobs += [(f"fig_traj_{k}.png", lambda k=k: fig_kind(k)) for k in mapgen.KINDS]
    for fname, make in jobs:
        fig, results = make()
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        path = os.path.join(OUT, fname)
        fig.savefig(path, dpi=140)
        plt.close(fig)
        summary = ", ".join(f"{n}={r.outcome}" for n, r in results.items())
        print(f"{fname}: {summary}")


if __name__ == "__main__":
    main()
