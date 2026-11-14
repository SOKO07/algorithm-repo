import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mapgen
import sim
from algo_straight import Straight


class SimTest(unittest.TestCase):
    def test_empty_map_arrives_with_straight_distance(self):
        r = sim.run(Straight(), mapgen.Map("open", 0, []))
        self.assertEqual(r.outcome, "arrived")
        d = math.dist(mapgen.START, mapgen.GOAL)
        self.assertAlmostEqual(r.distance, d - sim.GOAL_TOL, delta=0.5)
        self.assertEqual(r.steps, len(r.path) - 1)

    def test_obstacle_on_line_collides(self):
        m = mapgen.Map("open", 0, [(50.0, 50.0, 5.0)])
        self.assertEqual(sim.run(Straight(), m).outcome, "collision")

    def test_timeout(self):
        r = sim.run(Straight(), mapgen.Map("open", 0, []), max_steps=10)
        self.assertEqual(r.outcome, "timeout")
        self.assertEqual(r.steps, 10)

    def test_leaving_world_is_collision(self):
        self.assertTrue(sim.collides((-1.0, 50.0, 0.0), []))

    def test_collision_boundary(self):
        # touching distance r + ROBOT_RADIUS is not yet a collision
        gap = 5.0 + mapgen.ROBOT_RADIUS
        self.assertFalse(sim.collides((50.0 + gap, 50.0, 0), [(50.0, 50.0, 5.0)]))
        self.assertTrue(sim.collides((50.0 + gap - 0.01, 50.0, 0), [(50.0, 50.0, 5.0)]))

    def test_visibility_limited_by_range(self):
        near, far = (20.0, 30.0, 2.0), (90.0, 30.0, 2.0)
        vis = sim.visible_obstacles((20.0, 40.0, 0.0), [near, far])
        self.assertIn(near, vis)
        self.assertNotIn(far, vis)

    def test_border_visible_only_near_edge(self):
        self.assertEqual(sim.border_circles((50.0, 50.0, 0.0)), [])
        near = sim.border_circles((50.0, 5.0, 0.0))
        self.assertTrue(near)
        self.assertTrue(all(cy < 0 for _, cy, _ in near))  # only the y=0 edge

    def test_border_circles_agree_with_boundary_collision(self):
        # a robot just inside the collision limit touches a border circle
        for pose in ((50.0, sim.ROBOT_RADIUS + 0.2, 0.0), (99.0 - 0.2, 50.0, 0.0)):
            self.assertFalse(sim.collides(pose, sim.border_circles(pose)))
        for pose in ((50.0, sim.ROBOT_RADIUS - 0.3, 0.0), (99.3, 50.0, 0.0)):
            self.assertTrue(sim.collides(pose, sim.border_circles(pose)))

    def test_commands_are_clipped(self):
        p = sim.move((50.0, 50.0, 0.0), 99.0, 99.0)
        self.assertAlmostEqual(p[0], 50.0 + sim.V_MAX * math.cos(sim.OMEGA_MAX * sim.DT) * sim.DT)

    def test_same_map_same_result(self):
        m = mapgen.generate("open", 1001)
        a, b = sim.run(Straight(), m), sim.run(Straight(), m)
        self.assertEqual((a.outcome, a.steps, a.distance), (b.outcome, b.steps, b.distance))


if __name__ == "__main__":
    unittest.main()
