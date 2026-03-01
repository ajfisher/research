from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .simulator import Simulation, SimulationConfig, write_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MQTT desired-state protocol simulator (sleepy devices)")
    parser.add_argument("--num-devices", type=int, default=5)
    parser.add_argument("--wake-interval-base", type=int, default=3)
    parser.add_argument("--wake-interval-step", type=int, default=2)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--desired-updates", type=int, default=4)
    parser.add_argument("--desired-update-period", type=int, default=10)
    parser.add_argument("--disable-hello", action="store_true", help="Disable optional dev/<id>/hello publishes")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path("spikes/mqtt-desired-state-sim/results/runs"),
        help="Directory where per-run output folders are created",
    )
    parser.add_argument("--run-name", type=str, default="", help="Optional explicit run folder name")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    config = SimulationConfig(
        num_devices=args.num_devices,
        wake_interval_base=args.wake_interval_base,
        wake_interval_step=args.wake_interval_step,
        duration=args.duration,
        desired_updates=args.desired_updates,
        desired_update_period=args.desired_update_period,
        publish_hello=not args.disable_hello,
    )

    sim = Simulation(config)
    summary = sim.run()

    run_name = args.run_name.strip() or datetime.now().strftime("run-%Y%m%d-%H%M%S")
    out_dir = args.out_root / run_name
    write_outputs(out_dir, sim.events, summary)

    print(f"run_dir={out_dir}")
    print(f"events={out_dir / 'events.ndjson'}")
    print(f"summary={out_dir / 'summary.json'}")
    if summary.get("plot"):
        print(f"plot={out_dir / summary['plot']}")
    else:
        print("plot=not-generated")

    print(f"converged={summary['converged']}")
    print(f"monotonic_applied_v={summary['monotonic_applied_v']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
