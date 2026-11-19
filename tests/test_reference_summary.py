import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from reference_summary import load_references, percent_difference


class TestReferenceSummary(unittest.TestCase):
    def test_author_reported_values_are_loaded(self):
        values = load_references()
        self.assertEqual(values["Bare-metal standard"], 4.7)
        self.assertEqual(values["Bare-metal optimized"], 3.6)
        self.assertEqual(values["Zephyr RTOS System OFF"], 4.3)

    def test_percentage_comparisons(self):
        self.assertAlmostEqual(percent_difference(4.3, 4.7), -8.510638, places=5)
        self.assertAlmostEqual(percent_difference(4.3, 3.6), 19.444444, places=5)

    def test_zero_baseline_rejected(self):
        with self.assertRaises(ValueError):
            percent_difference(4.3, 0)


if __name__ == "__main__":
    unittest.main()
