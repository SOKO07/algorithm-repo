import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mapgen
import sim
from algo_dwa import DWA


class DWATest(unittest.TestCase):
    def test_empty_map_arrives(self):
        r = sim.run(DWA(), mapgen.Map("open", 0, []))
        self.assertEqual(r.outcome, "arrived")
        self.assertLess(r.distance, 135.0)

    def test_goes_around_obstacle_on_the_line(self):
        m = mapgen.Map("open", 0, [(50.0, 53.0, 6.0)])
        self.assertEqual(sim.run(DWA(), m).outcome, "arrived")

    def test_never_picks_a_colliding_trajectory_head_on(self):
        # an obstacle right in front: the chosen command must not hit it
        a = DWA()
        a.reset(mapgen.START, mapgen.GOAL)
        pose = (40.0, 40.0, 0.7854)
        v, w = a.step(pose, [(46.0, 46.0, 3.0)])
        nxt = sim.move(pose, v, w)
        self.assertFalse(sim.collides(nxt, [(46.0, 46.0, 3.0)]))

    def test_all_blocked_stops_and_turns(self):
        a = DWA()
        a.reset(mapgen.START, mapgen.GOAL)
        # ring leaves 0.02 of clearance: even the slowest circling move touches it
        ring = [(50.0 + 2.52 * c, 50.0 + 2.52 * s, 1.5)
                for c, s in ((1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7),
                             (-1, 0), (-0.7, -0.7), (0, -1), (0.7, -0.7))]
        v, w = a.step((50.0, 50.0, 0.0), ring)
        self.assertEqual(v, 0.0)

    def test_deterministic(self):
        m = mapgen.generate("cluttered", 1001)
        a, b = sim.run(DWA(), m), sim.run(DWA(), m)
        self.assertEqual((a.outcome, a.steps, a.distance), (b.outcome, b.steps, b.distance))


if __name__ == "__main__":
    unittest.main()
