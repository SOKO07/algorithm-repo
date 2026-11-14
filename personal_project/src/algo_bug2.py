"""Bug2 in continuous space.

Two modes:
  GO      head straight for the goal (the robot starts on the m-line, the
          segment start -> goal, and stays on it while going straight).
  FOLLOW  entered when an obstacle blocks the way (surface gap < `hit_dist`
          and the obstacle is in front).  Circle the nearest obstacle, keeping
          it on the LEFT at about `follow_dist` from the body, and remember
          the goal distance at the hit point.
Leave FOLLOW when the robot is back on the m-line (within `leave_tol`), is
strictly closer to the goal than at the hit point, and the way to the goal is
no longer blocked.

The world boundary arrives as ordinary virtual circles, so the same code
follows walls and borders.  No loop/unreachable detection: a robot that circles
forever ends as a timeout.
"""
import math

from mapgen import ROBOT_RADIUS
from sim import heading_command

# Frozen after tuning on the tuning seeds (see final_report.md).
HIT_DIST = 2.0
FOLLOW_DIST = 1.0
LEAVE_TOL = 2.0
KP = 0.5
PROGRESS = 0.5   # must be this much closer to the goal than at the hit point


class Bug2:
    name = "bug2"

    def __init__(self, hit_dist=HIT_DIST, follow_dist=FOLLOW_DIST,
                 leave_tol=LEAVE_TOL, kp=KP):
        self.hit_dist = hit_dist
        self.follow_dist = follow_dist
        self.leave_tol = leave_tol
        self.kp = kp

    def reset(self, start, goal):
        self.start, self.goal = start, goal
        self.mode = "GO"
        self.hit_goal_dist = math.inf
        sx, sy = start
        gx, gy = goal
        self.mline_len = math.hypot(gx - sx, gy - sy)

    def _dist_to_mline(self, x, y):
        sx, sy = self.start
        gx, gy = self.goal
        cross = (gx - sx) * (y - sy) - (gy - sy) * (x - sx)
        return abs(cross) / self.mline_len

    @staticmethod
    def _gap(x, y, obs):
        ox, oy, r = obs
        return math.hypot(x - ox, y - oy) - r - ROBOT_RADIUS

    def _blocked(self, x, y, goal_dir, visible):
        """An obstacle is close AND in front (toward the goal)."""
        for ox, oy, r in visible:
            if self._gap(x, y, (ox, oy, r)) >= self.hit_dist:
                continue
            tx, ty = ox - x, oy - y
            if tx * goal_dir[0] + ty * goal_dir[1] > 0:
                return True
        return False

    def step(self, pose, visible):
        x, y = pose[0], pose[1]
        gx, gy = self.goal[0] - x, self.goal[1] - y
        gd = math.hypot(gx, gy) or 1.0
        goal_dir = (gx / gd, gy / gd)
        blocked = self._blocked(x, y, goal_dir, visible)

        if self.mode == "GO":
            if blocked:
                self.mode = "FOLLOW"
                self.hit_goal_dist = gd
            else:
                return heading_command(pose, math.atan2(gy, gx))
        else:  # FOLLOW
            if (self._dist_to_mline(x, y) < self.leave_tol
                    and gd < self.hit_goal_dist - PROGRESS and not blocked):
                self.mode = "GO"
                return heading_command(pose, math.atan2(gy, gx))

        if not visible:
            return heading_command(pose, math.atan2(gy, gx))
        near = min(visible, key=lambda o: self._gap(x, y, o))
        ox, oy, r = near
        dx, dy = x - ox, y - oy
        c = math.hypot(dx, dy) or 1e-9
        nx, ny = dx / c, dy / c                  # outward from the obstacle
        tx, ty = -ny, nx                         # obstacle stays on the left
        err = self._gap(x, y, near) - self.follow_dist
        hx, hy = tx - self.kp * err * nx, ty - self.kp * err * ny
        return heading_command(pose, math.atan2(hy, hx))
