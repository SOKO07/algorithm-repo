"""2D simulator core: unicycle robot, collision check, common algorithm interface.

Algorithm interface (every algorithm implements this):

    class Algo:
        def reset(self, start, goal): ...
        def step(self, pose, visible): -> (v, omega)

    pose    = (x, y, theta)
    visible = [(ox, oy, r), ...]  obstacles within SENSE_RANGE of the robot
              (the full map is never given to the algorithm)

APF and Bug2 think in headings, so `heading_command` turns a desired heading
and speed into (v, omega) with the same limits DWA uses.
"""
import math
import time
from dataclasses import dataclass

from mapgen import GOAL, HEIGHT, ROBOT_RADIUS, START, WIDTH

DT = 0.1
V_MAX = 2.0          # units / s
OMEGA_MAX = 2.0      # rad / s
SENSE_RANGE = 15.0
GOAL_TOL = 1.5
MAX_STEPS = 3000


@dataclass
class Result:
    outcome: str          # "arrived" | "collision" | "timeout"
    distance: float       # path length of the robot center
    steps: int
    compute_time: float   # seconds spent inside algo.step only
    path: list


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def heading_command(pose, desired_heading, speed=V_MAX):
    """Shared heading -> (v, omega) controller for heading-based algorithms."""
    err = wrap(desired_heading - pose[2])
    omega = max(-OMEGA_MAX, min(OMEGA_MAX, err / DT))
    v = max(0.0, min(V_MAX, speed)) * max(0.0, math.cos(err))
    return v, omega


def move(pose, v, omega):
    """One unicycle step with clipped commands."""
    v = max(0.0, min(V_MAX, v))
    omega = max(-OMEGA_MAX, min(OMEGA_MAX, omega))
    x, y, th = pose
    th = wrap(th + omega * DT)
    return (x + v * math.cos(th) * DT, y + v * math.sin(th) * DT, th)


def collides(pose, obstacles):
    x, y = pose[0], pose[1]
    if not (ROBOT_RADIUS <= x <= WIDTH - ROBOT_RADIUS
            and ROBOT_RADIUS <= y <= HEIGHT - ROBOT_RADIUS):
        return True  # leaving the world counts as a collision
    return any(math.hypot(x - ox, y - oy) < r + ROBOT_RADIUS
               for ox, oy, r in obstacles)


BORDER_R = 2.0
BORDER_STEP = 1.5


def border_circles(pose):
    """Virtual circles tangent to the world edges, only those within sense range.

    The world boundary is treated as an obstacle: the sensor reports it like
    any other circle, and leaving the world still counts as a collision.
    """
    x, y = pose[0], pose[1]
    out = []
    # (edge coordinate, horizontal?) -- horizontal edges are y=0 and y=HEIGHT
    for edge, horizontal in ((0.0, True), (HEIGHT, True), (0.0, False), (WIDTH, False)):
        across = y if horizontal else x   # robot's distance axis to the edge
        along = x if horizontal else y    # robot's coordinate along the edge
        if abs(across - edge) > SENSE_RANGE + BORDER_R:
            continue
        lo = max(0.0, along - SENSE_RANGE - BORDER_R)
        hi = min(WIDTH, along + SENSE_RANGE + BORDER_R)
        off = -BORDER_R if edge == 0.0 else edge + BORDER_R
        t = math.floor(lo / BORDER_STEP) * BORDER_STEP
        while t <= hi:
            cx, cy = (t, off) if horizontal else (off, t)
            if math.hypot(x - cx, y - cy) - BORDER_R <= SENSE_RANGE:
                out.append((cx, cy, BORDER_R))
            t += BORDER_STEP
    return out


def visible_obstacles(pose, obstacles):
    vis = [(ox, oy, r) for ox, oy, r in obstacles
           if math.hypot(pose[0] - ox, pose[1] - oy) - r <= SENSE_RANGE]
    return vis + border_circles(pose)


def run(algo, game_map, max_steps=MAX_STEPS):
    obstacles = game_map.obstacles
    pose = (START[0], START[1], math.atan2(GOAL[1] - START[1], GOAL[0] - START[0]))
    algo.reset(START, GOAL)
    path = [pose[:2]]
    dist = 0.0
    compute = 0.0
    for step in range(1, max_steps + 1):
        vis = visible_obstacles(pose, obstacles)
        t0 = time.perf_counter()
        v, omega = algo.step(pose, vis)
        compute += time.perf_counter() - t0
        new = move(pose, v, omega)
        dist += math.hypot(new[0] - pose[0], new[1] - pose[1])
        pose = new
        path.append(pose[:2])
        if collides(pose, obstacles):
            return Result("collision", dist, step, compute, path)
        if math.hypot(pose[0] - GOAL[0], pose[1] - GOAL[1]) <= GOAL_TOL:
            return Result("arrived", dist, step, compute, path)
    return Result("timeout", dist, max_steps, compute, path)
