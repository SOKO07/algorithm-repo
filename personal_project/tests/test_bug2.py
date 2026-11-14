import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mapgen
import sim
from algo_bug2 import Bug2


def wall(half, step=3, r=2.0):
    """Wall perpendicular to the start-goal line, centered at (50, 50)."""
    s = 2 ** -0.5
    return [(50.0 + s * t, 50.0 - s * t, r) for t in range(-half, half + 1, step)]


class Bug2Test(unittest.TestCase):
    def test_empty_map_goes_straight(self):
        r = sim.run(Bug2(), mapgen.Map("open", 0, []))
        self.assertEqual(r.outcome, "arrived")
        self.assertLess(r.distance, 127.0)

    def test_goes_around_obstacle_on_the_line(self):
        m = mapgen.Map("open", 0, [(50.0, 50.0, 8.0)])
        r = sim.run(Bug2(), m)
        self.assertEqual(r.outcome, "arrived")

    def test_gets_around_long_wall(self):
        # APF stalls on this wall; Bug2 follows its boundary around the end.
        r = sim.run(Bug2(), mapgen.Map("open", 0, wall(20)))
        self.assertEqual(r.outcome, "arrived")

    def test_enters_follow_mode_at_obstacle(self):
        a = Bug2()
        a.reset(mapgen.START, mapgen.GOAL)
        a.step((46.0, 46.0, 0.8), [(50.0, 50.0, 5.0)])
        self.assertEqual(a.mode, "FOLLOW")

    def test_ignores_obstacle_behind(self):
        a = Bug2()
        a.reset(mapgen.START, mapgen.GOAL)
        a.step((50.0, 50.0, 0.8), [(48.0, 48.0, 1.0)])
        self.assertEqual(a.mode, "GO")

    def test_deterministic(self):
        m = mapgen.generate("cluttered", 1001)
        a, b = sim.run(Bug2(), m), sim.run(Bug2(), m)
        self.assertEqual((a.outcome, a.steps, a.distance), (b.outcome, b.steps, b.distance))


if __name__ == "__main__":
    unittest.main()
