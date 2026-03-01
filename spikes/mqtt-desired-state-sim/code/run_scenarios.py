from __future__ import annotations

import argparse
from pathlib import Path

from mqttsim.batch import run_retries
from mqttsim.simulator import SimulationConfig


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run multiple gremlin scenarios with retries and aggregate results")
    p.add_argument("--out-root", type=Path, default=Path("spikes/mqtt-desired-state-sim/results/scenarios"))
    p.add_argument("--retries", type=int, default=20)
    return p.parse_args()


def main() -> int:
    args = parse_args()

    scenarios: dict[str, SimulationConfig] = {
        "baseline": SimulationConfig(seed=1, duration=120, num_devices=20, awake_duration=20, min_delay=0, max_delay=0, loss_rate=0.0, dup_rate=0.0),
        "lossy": SimulationConfig(seed=10, duration=200, num_devices=50, awake_duration=40, min_delay=0, max_delay=10, loss_rate=0.2, dup_rate=0.0),
        "delay_short_awake": SimulationConfig(seed=100, duration=200, num_devices=50, awake_duration=1, min_delay=5, max_delay=20, loss_rate=0.0, dup_rate=0.0),
        "dup_and_loss": SimulationConfig(seed=200, duration=200, num_devices=50, awake_duration=40, min_delay=0, max_delay=20, loss_rate=0.2, dup_rate=0.5),
        "broker_restart_mid": SimulationConfig(seed=300, duration=200, num_devices=50, awake_duration=40, min_delay=0, max_delay=20, loss_rate=0.1, dup_rate=0.2, broker_restart_at=77, republish_on_hello=True),
        "epoch_reset_bug": SimulationConfig(seed=400, duration=200, num_devices=50, awake_duration=40, min_delay=0, max_delay=20, loss_rate=0.05, dup_rate=0.1, controller_epoch_reset_at=100, controller_epoch_reset_mode="reset0"),
        "epoch_increment_ok": SimulationConfig(seed=500, duration=200, num_devices=50, awake_duration=40, min_delay=0, max_delay=20, loss_rate=0.05, dup_rate=0.1, controller_epoch_reset_at=100, controller_epoch_reset_mode="increment"),
    }

    for name, cfg in scenarios.items():
        agg = run_retries(scenario_name=name, base_config=cfg, retries=args.retries, out_root=args.out_root)
        print(f"{name}: convergence_rate={agg['convergence_rate']:.2f} stale_mean={agg['stale_device_count']['mean']}")

    print(f"wrote to {args.out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
