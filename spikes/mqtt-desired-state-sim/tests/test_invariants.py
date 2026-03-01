from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from mqttsim.simulator import Simulation, SimulationConfig  # noqa: E402


class InvariantTests(unittest.TestCase):
    def test_monotonic_applied_v(self) -> None:
        config = SimulationConfig(
            num_devices=4,
            duration=50,
            desired_updates=5,
            desired_update_period=7,
            wake_interval_base=2,
            wake_interval_step=1,
        )
        sim = Simulation(config)
        summary = sim.run()

        self.assertTrue(summary["monotonic_applied_ver"])
        self.assertIn("broker_metrics", summary)
        self.assertIn("published_messages", summary["broker_metrics"])

        # Extra guard: validate from raw apply events as well.
        by_device: dict[str, list[int]] = {}
        for event in sim.events:
            if event["kind"] == "apply":
                by_device.setdefault(event["device_id"], []).append(int(event["applied_ver"]))

        for versions in by_device.values():
            self.assertEqual(versions, sorted(versions))

    def test_convergence_correctness(self) -> None:
        config = SimulationConfig(
            num_devices=3,
            duration=80,
            desired_updates=4,
            desired_update_period=10,
            wake_interval_base=3,
            wake_interval_step=3,
        )
        sim = Simulation(config)
        summary = sim.run()

        self.assertTrue(summary["converged"])
        self.assertEqual(summary["final_desired"]["v"], 4)

        for _, metrics in summary["devices"].items():
            self.assertTrue(metrics["converged"])
            self.assertEqual(metrics["applied_ver"], summary["final_desired"]["ver"])
            # Metrics should be present
            self.assertIn("stale_wake_ratio", metrics)
            self.assertIn("time_to_converge_ticks", metrics)


if __name__ == "__main__":
    unittest.main()
