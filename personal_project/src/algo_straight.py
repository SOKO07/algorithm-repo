"""Dummy algorithm: drive straight at the goal, ignoring obstacles.

Only used to check the simulator (arrives on empty maps, collides on blocked ones).
"""
import math

from sim import heading_command


class Straight:
    name = "straight"

    def reset(self, start, goal):
        self.goal = goal

    def step(self, pose, visible):
        h = math.atan2(self.goal[1] - pose[1], self.goal[0] - pose[0])
        return heading_command(pose, h)
