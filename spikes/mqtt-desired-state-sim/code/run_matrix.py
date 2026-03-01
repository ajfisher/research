from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mqttsim.batch import run_retries
from mqttsim.simulator import SimulationConfig


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Matrix sweep: vary device_count and retries to map breakage")
    p.add_argument("--out-root", type=Path, default=Path("spikes/mqtt-desired-state-sim/results/matrix"))
    p.add_argument("--device-min", type=int, default=25)
    p.add_argument("--device-max", type=int, default=300)
    p.add_argument("--device-step", type=int, default=25)
    p.add_argument(
        "--retries",
        type=str,
        default="10,25,50",
        help="Comma-separated retry counts to run (e.g. 10,25,50)",
    )
    return p.parse_args()


def scenarios() -> dict[str, SimulationConfig]:
    return {
        # Keep these moderately hard; we want to see breakpoints.
        "lossy": SimulationConfig(seed=10, duration=250, awake_duration=40, min_delay=0, max_delay=10, loss_rate=0.2, dup_rate=0.0),
        "dup_and_loss": SimulationConfig(seed=200, duration=250, awake_duration=40, min_delay=0, max_delay=20, loss_rate=0.2, dup_rate=0.5),
        "broker_restart_mid": SimulationConfig(seed=300, duration=250, awake_duration=40, min_delay=0, max_delay=20, loss_rate=0.1, dup_rate=0.2, broker_restart_at=77, republish_on_hello=True),
        "delay_short_awake": SimulationConfig(seed=100, duration=250, awake_duration=1, min_delay=5, max_delay=20, loss_rate=0.0, dup_rate=0.0),
    }


def main() -> int:
    args = parse_args()
    retry_levels = [int(x.strip()) for x in args.retries.split(",") if x.strip()]
    device_counts = list(range(args.device_min, args.device_max + 1, args.device_step))

    out_root = args.out_root
    out_root.mkdir(parents=True, exist_ok=True)

    meta = {
        "device_counts": device_counts,
        "retry_levels": retry_levels,
        "scenarios": {name: asdict(cfg) for name, cfg in scenarios().items()},
    }
    (out_root / "matrix_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows: list[dict[str, Any]] = []

    for scen_name, base in scenarios().items():
        for retries in retry_levels:
            for ndev in device_counts:
                cfg = SimulationConfig(**asdict(base))
                cfg.num_devices = ndev

                cell_name = f"{scen_name}/devices-{ndev:04d}/retries-{retries:03d}"
                agg = run_retries(
                    scenario_name=cell_name,
                    base_config=cfg,
                    retries=retries,
                    out_root=out_root,
                    write_full_artifacts=False,
                )

                rows.append(
                    {
                        "scenario": scen_name,
                        "num_devices": ndev,
                        "retries": retries,
                        "convergence_rate": agg.get("convergence_rate"),
                        "stale_device_mean": agg.get("stale_device_count", {}).get("mean"),
                        "stale_device_p95": agg.get("stale_device_count", {}).get("p95"),
                        "ttc_p95": agg.get("time_to_converge_ticks", {}).get("p95"),
                        "stale_wake_ratio_p95": agg.get("stale_wake_ratio", {}).get("p95"),
                    }
                )

    (out_root / "matrix_rows.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Simple CSV for quick plotting elsewhere.
    csv_lines = [
        "scenario,num_devices,retries,convergence_rate,stale_device_mean,stale_device_p95,ttc_p95,stale_wake_ratio_p95"
    ]
    for r in rows:
        csv_lines.append(
            f"{r['scenario']},{r['num_devices']},{r['retries']},{r['convergence_rate']},{r['stale_device_mean']},{r['stale_device_p95']},{r['ttc_p95']},{r['stale_wake_ratio_p95']}"
        )
    (out_root / "matrix.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    print(f"wrote matrix to {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
