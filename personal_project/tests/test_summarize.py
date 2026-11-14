import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import summarize


class SummarizeTest(unittest.TestCase):
    def test_wilson_is_symmetric_at_half(self):
        lo, hi = summarize.wilson(50, 100)
        self.assertAlmostEqual(lo + hi, 1.0, places=9)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)

    def test_wilson_bounds(self):
        lo, hi = summarize.wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        lo, hi = summarize.wilson(10, 10)
        self.assertLessEqual(hi, 1.0 + 1e-12)
        self.assertLess(lo, 1.0)

    def test_mcnemar_known_values(self):
        self.assertAlmostEqual(summarize.mcnemar_exact(0, 6), 2 / 64)
        self.assertEqual(summarize.mcnemar_exact(5, 5), 1.0)
        self.assertEqual(summarize.mcnemar_exact(0, 0), 1.0)
        self.assertEqual(summarize.mcnemar_exact(3, 1), summarize.mcnemar_exact(1, 3))

    def test_cost_table_uses_total_time_over_total_steps(self):
        rows = [
            {"kind": "open", "algo": "APF", "steps": "100", "compute_time": "0.1"},
            {"kind": "open", "algo": "APF", "steps": "300", "compute_time": "0.3"},
        ]
        text = chr(10).join(summarize.table_cost(rows, ["open"]))
        # (0.1 + 0.3) s / 400 steps = 1.000 ms per step
        self.assertIn("1.000", text)
        self.assertIn("| open | APF | 2 | 200 | 0.200 | 1.000 |", text)


if __name__ == "__main__":
    unittest.main()
