"""Dynamic window approach (DWA).

Every step, sample (v, omega) candidates, roll each one forward for `t_pred`
seconds with the simulator's own kinematics, drop candidates that touch an
obstacle, and pick the best score:

    score = ALPHA * heading + beta * clearance + gamma * velocity

    heading    1 - |angle from the end pose to the goal| / pi
    clearance  smallest body-to-obstacle gap along the path, capped, in [0, 1]
    velocity   v / V_MAX

Simplification: the simulator has no acceleration limits (APF and Bug2 may turn
at full rate instantly), so the dynamic window is the whole speed range
[0, V_MAX] x [-OMEGA_MAX, OMEGA_MAX].  DWA keeps its own trait of predicting
and scoring trajectories.  Like APF it only sees the local picture; there is no
global escape from a local minimum.  If every candidate collides the robot
stands still and turns toward the goal.
"""
import math

from mapgen import ROBOT_RADIUS
from sim import DT, OMEGA_MAX, V_MAX, wrap

# Frozen after tuning on the tuning seeds (see final_report.md).
BETA = 1.0
GAMMA = 2.0
T_PRED = 1.5
ALPHA = 1.0
N_V = 5
N_W = 15
PRED_DT = DT  # same step as the simulator, so predictions match what is executed
CLEAR_CAP = 3.0


class DWA:
    name = "dwa"

    def __init__(self, beta=BETA, gamma=GAMMA, t_pred=T_PRED):
        self.beta = beta
        self.gamma = gamma
        self.t_pred = t_pred
        n = max(1, round(t_pred / PRED_DT))
        self.n_pred = n
        # no standstill candidate: v = 0 would beat every moving one near obstacles
        self.vs = [V_MAX * i / N_V for i in range(1, N_V + 1)]
        self.ws = [-OMEGA_MAX + 2 * OMEGA_MAX * j / (N_W - 1) for j in range(N_W)]

    def reset(self, start, goal):
        self.goal = goal

    def step(self, pose, visible):
        x0, y0, th0 = pose
        gx, gy = self.goal
        reach = V_MAX * self.t_pred + ROBOT_RADIUS + CLEAR_CAP
        near = [(ox, oy, r) for ox, oy, r in visible
                if math.hypot(x0 - ox, y0 - oy) - r <= reach]
        best, best_cmd = -math.inf, None
        for v in self.vs:
            for w in self.ws:
                x, y, th = x0, y0, th0
                min_gap = math.inf
                hit = False
                for _ in range(self.n_pred):
                    th = wrap(th + w * PRED_DT)
                    x += v * math.cos(th) * PRED_DT
                    y += v * math.sin(th) * PRED_DT
                    for ox, oy, r in near:
                        gap = math.hypot(x - ox, y - oy) - r - ROBOT_RADIUS
                        if gap <= 0.0:
                            hit = True
                            break
                        if gap < min_gap:
                            min_gap = gap
                    if hit:
                        break
                if hit:
                    continue
                heading = 1.0 - abs(wrap(math.atan2(gy - y, gx - x) - th)) / math.pi
                clearance = min(min_gap, CLEAR_CAP) / CLEAR_CAP
                score = ALPHA * heading + self.beta * clearance + self.gamma * v / V_MAX
                if score > best:
                    best, best_cmd = score, (v, w)
        if best_cmd is None:  # every candidate collides: stop and turn to the goal
            err = wrap(math.atan2(gy - y0, gx - x0) - th0)
            return 0.0, max(-OMEGA_MAX, min(OMEGA_MAX, err / DT))
        return best_cmd
