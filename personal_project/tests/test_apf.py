import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mapgen
import sim
from algo_apf import APF


class APFTest(unittest.TestCase):
    def test_empty_map_arrives(self):
        r = sim.run(APF(), mapgen.Map("open", 0, []))
        self.assertEqual(r.outcome, "arrived")

    def test_avoids_off_axis_obstacle(self):
        # obstacle slightly off the straight line: a straight drive would hit it
        m = mapgen.Map("open", 0, [(50.0, 53.0, 5.0)])
        r = sim.run(APF(), m)
        self.assertEqual(r.outcome, "arrived")

    def test_wall_across_path_is_local_minimum(self):
        # long wall perpendicular to the start-goal line: attraction and
        # repulsion cancel in front of it and the robot never gets around.
        s = 2 ** -0.5
        wall = [(50.0 + s * t, 50.0 - s * t, 2.0) for t in range(-20, 21, 3)]
        r = sim.run(APF(), mapgen.Map("open", 0, wall), max_steps=2000)
        self.assertEqual(r.outcome, "timeout")

    def test_repulsion_points_away(self):
        a = APF()
        a.reset(mapgen.START, mapgen.GOAL)
        # obstacle right of the robot (robot heading +x toward a goal on +x):
        a.goal = (100.0, 0.0)
        v, omega = a.step((0.0, 0.0, 0.0), [(5.0, -1.0, 2.0)])
        self.assertGreater(omega, 0.0)  # turns left, away from obstacle below

    def test_deterministic(self):
        m = mapgen.generate("cluttered", 1001)
        a, b = sim.run(APF(), m), sim.run(APF(), m)
        self.assertEqual((a.outcome, a.steps, a.distance), (b.outcome, b.steps, b.distance))


if __name__ == "__main__":
    unittest.main()
