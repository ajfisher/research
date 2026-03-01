## 2026-03-01 15:55 AEDT - Spike setup

Created `spikes/mqtt-desired-state-sim/` with self-contained structure (`code/`, `tests/`, `results/`, `data/`, `diffs/`).

## 2026-03-01 15:58 AEDT - Protocol and simulator design

Defined device-agnostic topic contract:
- `dev/<id>/desired` retained
- `dev/<id>/telemetry` non-retained
- optional `dev/<id>/hello`

Chose deterministic time-step simulation and an in-process broker that supports:
- retained payload replay on subscribe
- exact-topic subscriptions
- immediate in-process delivery

## 2026-03-01 16:03 AEDT - Implementation

Implemented:
- `code/mqttsim/simulator.py` (broker, device model, simulation driver, output writer, optional plotting)
- `code/mqttsim/cli.py` and `code/run_sim.py` for command-line runs

Output behavior:
- Creates per-run directory under `results/runs/`
- Writes `events.ndjson` and `summary.json`
- Generates `applied_versions.png` (matplotlib if available, otherwise pure-Python fallback)

## 2026-03-01 16:06 AEDT - Validation

Added unit tests:
- `test_monotonic_applied_v`
- `test_convergence_correctness`

Both tests validate protocol invariants against simulation outputs.

## 2026-03-01 16:08 AEDT - Documentation and task index

Created:
- `PROTOCOL.md`
- `report.md`
- `README.md` with example commands

Planned repo update:
- add active task entry in `TASKS.md`.

## 2026-03-01 16:12 AEDT - Plot fallback and sample run

Observed `matplotlib` missing in environment. Implemented pure-Python PNG plotting fallback so each run still produces `applied_versions.png` with no extra dependencies.

Validation:
- Re-ran unit tests (`2 passed`)
- Generated sample output in `results/runs/sample-run/` containing:
  - `events.ndjson`
  - `summary.json`
  - `applied_versions.png`
