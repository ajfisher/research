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
    parser.add_argument("--awake-duration", type=int, default=1, help="How many ticks a device stays awake")
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--desired-updates", type=int, default=4)
    parser.add_argument("--desired-update-period", type=int, default=10)
    parser.add_argument("--disable-hello", action="store_true", help="Disable optional dev/<id>/hello publishes")

    # Gremlin knobs
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--loss", type=float, default=0.0, help="Per-delivery loss rate in [0,1]")
    parser.add_argument("--min-delay", type=int, default=0, help="Min delivery delay (ticks)")
    parser.add_argument("--max-delay", type=int, default=0, help="Max delivery delay (ticks)")
    parser.add_argument("--dup", type=float, default=0.0, help="Duplicate delivery rate in [0,1]")
    parser.add_argument("--naive-last-write", action="store_true", help="BUG MODE: during a wake window use last-received desired (can miss newest under reordering)")
    parser.add_argument("--broker-restart-at", type=int, default=-1, help="Tick to reset live sessions/in-flight messages (-1 disables)")

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
        awake_duration=args.awake_duration,
        duration=args.duration,
        desired_updates=args.desired_updates,
        desired_update_period=args.desired_update_period,
        publish_hello=not args.disable_hello,
        seed=args.seed,
        loss_rate=args.loss,
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        dup_rate=args.dup,
        naive_last_write=args.naive_last_write,
        broker_restart_at=None if args.broker_restart_at < 0 else args.broker_restart_at,
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
