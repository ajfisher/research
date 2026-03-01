# Report: MQTT Desired-State Protocol Simulator (Sleepy Devices)

## Objective
Validate a minimal retained desired-state protocol for sleepy devices and verify convergence/monotonicity invariants.

## Method
- Built a pure-Python in-process MQTT-like broker with retained message support.
- Simulated periodic desired-state updates from a control plane.
- Simulated devices that wake periodically, fetch retained desired state, apply monotonic versions, and emit telemetry.
- Captured run outputs in per-run folders with `events.ndjson` and `summary.json`.
- Added plotting output (`applied_versions.png`), using `matplotlib` when available and a pure-Python fallback otherwise.

## Key Findings
- Retained desired topics reliably bridge offline periods: devices waking later still receive latest desired version.
- Telemetry must remain non-retained to avoid stale liveness/status interpretation.
- Monotonic `applied_v` and eventual convergence can be validated with deterministic tests.

## Artifacts
- Protocol spec: `PROTOCOL.md`
- Simulator: `code/mqttsim/`
- CLI entrypoint: `code/run_sim.py`
- Tests: `tests/test_invariants.py`
- Run outputs: `results/runs/<run-name>/`
