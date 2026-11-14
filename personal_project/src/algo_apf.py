"""Artificial potential field (APF).

The goal pulls with a constant-magnitude force (unit vector toward the goal).
Each visible obstacle within `d0` of the robot body pushes away with the
classic repulsive gradient  k_rep * (1/d - 1/d0) / d^2.  The robot heads along
the resultant force.  Only the ratio k_rep / k_att matters for the heading, so
k_att is fixed to 1.

No escape heuristic is added: a local minimum (forces cancel) is part of what
the comparison is meant to show.  When the resultant is ~0 the robot stops and
the run ends as a timeout.
"""
import math

from mapgen import ROBOT_RADIUS
from sim import heading_command

# Frozen after tuning on the tuning seeds (see final_report.md).
K_REP = 2.5
D0 = 12.0
EPS_FORCE = 1e-6
MIN_DIST = 0.05


class APF:
    name = "apf"

    def __init__(self, k_rep=K_REP, d0=D0):
        self.k_rep = k_rep
        self.d0 = d0

    def reset(self, start, goal):
        self.goal = goal

    def step(self, pose, visible):
        x, y = pose[0], pose[1]
        gx, gy = self.goal[0] - x, self.goal[1] - y
        gd = math.hypot(gx, gy) or 1.0
        fx, fy = gx / gd, gy / gd
        for ox, oy, r in visible:
            dx, dy = x - ox, y - oy
            c = math.hypot(dx, dy) or 1e-9
            d = max(c - r - ROBOT_RADIUS, MIN_DIST)  # gap between surfaces
            if d >= self.d0:
                continue
            mag = self.k_rep * (1.0 / d - 1.0 / self.d0) / (d * d)
            fx += mag * dx / c
            fy += mag * dy / c
        if math.hypot(fx, fy) < EPS_FORCE:
            return 0.0, 0.0
        return heading_command(pose, math.atan2(fy, fx))
