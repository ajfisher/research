from __future__ import annotations

import json
import statistics
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .io_utils import write_summary
from .simulator import Simulation, SimulationConfig, write_outputs


def run_retries(
    *,
    scenario_name: str,
    base_config: SimulationConfig,
    retries: int,
    out_root: Path,
    write_full_artifacts: bool = False,
) -> dict[str, Any]:
    """Run a scenario multiple times with different seeds and write aggregate metrics.

    By default this writes only per-retry `summary.json` (fast + small). When
    `write_full_artifacts=True`, writes full artifacts (`events.ndjson`, plot PNG, etc.).
    """

    scenario_dir = out_root / scenario_name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []

    for i in range(retries):
        cfg = SimulationConfig(**asdict(base_config))
        cfg.seed = int(base_config.seed) + i

        sim = Simulation(cfg)
        summary = sim.run()
        run_dir = scenario_dir / f"rep-{i:04d}"
        if write_full_artifacts:
            write_outputs(run_dir, sim.events, summary)
        else:
            write_summary(run_dir, summary)
        summaries.append(summary)

    stale_counts = [int(s.get("stale_device_count", 0)) for s in summaries]
    converged_flags = [bool(s.get("converged", False)) for s in summaries]

    # Flatten per-device metrics across retries
    ttc: list[int] = []
    stale_wake_ratios: list[float] = []
    for s in summaries:
        for d in s.get("devices", {}).values():
            if d.get("time_to_converge_ticks") is not None:
                ttc.append(int(d["time_to_converge_ticks"]))
            if d.get("stale_wake_ratio") is not None:
                stale_wake_ratios.append(float(d["stale_wake_ratio"]))

    def dist_int(values: list[int]) -> dict[str, Any]:
        if not values:
            return {"min": None, "max": None, "mean": None, "median": None, "p95": None, "values": []}
        p95 = statistics.quantiles(values, n=20)[-1] if len(values) >= 2 else values[0]
        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p95": p95,
            "values": values,
        }

    def dist_float(values: list[float]) -> dict[str, Any]:
        if not values:
            return {"min": None, "max": None, "mean": None, "median": None, "p95": None, "values": []}
        p95 = statistics.quantiles(values, n=20)[-1] if len(values) >= 2 else values[0]
        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p95": p95,
            "values": values,
        }

    agg = {
        "scenario": scenario_name,
        "ran_at": datetime.now().isoformat(),
        "retries": retries,
        "base_config": asdict(base_config),
        "convergence_rate": sum(1 for c in converged_flags if c) / max(1, len(converged_flags)),
        "stale_device_count": dist_int(stale_counts),
        "time_to_converge_ticks": dist_int(ttc),
        "stale_wake_ratio": dist_float(stale_wake_ratios),
    }

    (scenario_dir / "aggregate.json").write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return agg
