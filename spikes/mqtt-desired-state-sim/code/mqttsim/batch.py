from __future__ import annotations

import json
import statistics
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .simulator import Simulation, SimulationConfig, write_outputs


def run_retries(
    *,
    scenario_name: str,
    base_config: SimulationConfig,
    retries: int,
    out_root: Path,
) -> dict[str, Any]:
    """Run a scenario multiple times with different seeds and write aggregate metrics."""

    scenario_dir = out_root / scenario_name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []

    for i in range(retries):
        cfg = SimulationConfig(**asdict(base_config))
        cfg.seed = int(base_config.seed) + i

        sim = Simulation(cfg)
        summary = sim.run()
        run_dir = scenario_dir / f"rep-{i:04d}"
        write_outputs(run_dir, sim.events, summary)
        summaries.append(summary)

    stale_counts = [int(s.get("stale_device_count", 0)) for s in summaries]
    converged_flags = [bool(s.get("converged", False)) for s in summaries]

    agg = {
        "scenario": scenario_name,
        "ran_at": datetime.now().isoformat(),
        "retries": retries,
        "base_config": asdict(base_config),
        "convergence_rate": sum(1 for c in converged_flags if c) / max(1, len(converged_flags)),
        "stale_device_count": {
            "min": min(stale_counts) if stale_counts else None,
            "max": max(stale_counts) if stale_counts else None,
            "mean": statistics.mean(stale_counts) if stale_counts else None,
            "median": statistics.median(stale_counts) if stale_counts else None,
            "p95": statistics.quantiles(stale_counts, n=20)[-1] if len(stale_counts) >= 2 else (stale_counts[0] if stale_counts else None),
            "values": stale_counts,
        },
    }

    (scenario_dir / "aggregate.json").write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return agg
