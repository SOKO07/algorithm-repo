import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mapgen
import reference


class ReferenceTest(unittest.TestCase):
    def test_empty_map_is_about_straight_distance(self):
        d = math.dist(mapgen.START, mapgen.GOAL)
        got = reference.shortest_length([])
        self.assertGreaterEqual(got, d - 1.0)
        self.assertLess(got, d * 1.02)

    def test_obstacle_makes_it_longer(self):
        free = reference.shortest_length([])
        blocked = reference.shortest_length([(50.0, 50.0, 10.0)])
        self.assertGreater(blocked, free + 3.0)

    def test_unreachable_returns_none(self):
        wall = [(x + 0.0, y + 0.0, 2.0) for x in (50,) for y in range(0, 101, 3)]
        self.assertIsNone(reference.shortest_length(wall))

    def test_solvable_maps_have_a_length(self):
        m = mapgen.generate("cluttered", 1001)
        self.assertIsNotNone(reference.shortest_length(m.obstacles))


if __name__ == "__main__":
    unittest.main()
