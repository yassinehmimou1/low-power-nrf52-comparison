import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "analysis" / "power_analysis.py"
SPEC = importlib.util.spec_from_file_location("power_analysis", SCRIPT)
power_analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = power_analysis
SPEC.loader.exec_module(power_analysis)


class PowerAnalysisTests(unittest.TestCase):
    def sample(self, t, current=1.0, voltage=3.0, impl="Bare-Metal", origin="MEASURED",
               run_id="unspecified", phase="unspecified"):
        return power_analysis.Sample(t, current, voltage, impl, origin, run_id, phase)

    def test_constant_current_and_voltage(self):
        metrics = power_analysis.calculate_metrics(
            [self.sample(0), self.sample(10)], capacity_mah=1000, period_s=5
        )
        self.assertAlmostEqual(metrics.mean_current_mA, 1.0)
        self.assertAlmostEqual(metrics.mean_power_mW, 3.0)
        self.assertAlmostEqual(metrics.peak_current_mA, 1.0)
        self.assertAlmostEqual(metrics.charge_mAh, 10.0 / 3600.0)
        self.assertAlmostEqual(metrics.energy_mWh, 30.0 / 3600.0)
        self.assertAlmostEqual(metrics.energy_per_cycle_mJ, 15.0)
        self.assertAlmostEqual(metrics.autonomy_h_ideal, 1000.0)

    def test_trapezoidal_current(self):
        metrics = power_analysis.calculate_metrics(
            [self.sample(0, 0.0), self.sample(2, 2.0)], capacity_mah=None, period_s=5
        )
        self.assertAlmostEqual(metrics.mean_current_mA, 1.0)

    def test_duplicate_timestamps_rejected(self):
        with self.assertRaises(ValueError):
            power_analysis.calculate_metrics(
                [self.sample(1), self.sample(1)], capacity_mah=None, period_s=5
            )

    def test_out_of_order_timestamps_rejected(self):
        with self.assertRaises(ValueError):
            power_analysis.calculate_metrics(
                [self.sample(2), self.sample(1)], capacity_mah=None, period_s=5
            )

    def test_simulated_origin_is_kept_separate(self):
        rows = [self.sample(0, origin="SIMULATED"), self.sample(1, origin="SIMULATED")]
        metrics = power_analysis.calculate_metrics(rows, capacity_mah=None, period_s=5)
        report = power_analysis.render_report([("Bare-Metal", "SIMULATED", "synthetic-test", metrics)], None, 5)
        self.assertIn("SIMULATED data", report)

    def test_phase_current_is_reported_separately(self):
        samples = [
            self.sample(0, 1.0, phase="idle"),
            self.sample(1, 1.0, phase="idle"),
            self.sample(2, 3.0, phase="active"),
            self.sample(3, 3.0, phase="active"),
        ]
        metrics = power_analysis.calculate_metrics(samples, capacity_mah=None, period_s=5)
        phases = {item.phase: item for item in metrics.phase_metrics}
        self.assertAlmostEqual(phases["idle"].mean_current_mA, 1.0)
        self.assertAlmostEqual(phases["active"].mean_current_mA, 3.0)
        self.assertAlmostEqual(phases["TRANSITION"].duration_s, 1.0)

    def test_csv_requires_origin_and_valid_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "input.csv"
            path.write_text(
                "timestamp_s,implementation,current_mA,voltage_V,data_origin\n"
                "0,Bare-Metal,1,3,MEASURED\n"
                "1,Bare-Metal,1,3,MEASURED\n",
                encoding="utf-8",
            )
            self.assertEqual(len(power_analysis.load_samples(path)), 2)


if __name__ == "__main__":
    unittest.main()
