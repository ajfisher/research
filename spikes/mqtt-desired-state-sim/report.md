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
- Retained desired topics bridge offline periods: devices waking later can still receive the latest desired version.
- Telemetry must remain non-retained to avoid stale liveness/status interpretation.
- Monotonic `applied_v` is easy to guarantee with a single device rule: apply only when `desired.v > applied_v`.

### Gremlin breakage 1: simulated delay + short wake windows
When we introduce delivery delay (e.g. 2–5 ticks) and devices only stay awake for 1 tick, many devices fail to converge within the simulation horizon.

This isn’t a “protocol is wrong” result so much as a reminder that **the physical awake window bounds what you can receive**. In practice you’d address this by:
- keeping the radio on long enough to receive retained replay, or
- requesting state explicitly after wake, or
- using QoS/session semantics (outside the scope of this spike).

The simulator demonstrates this failure mode and the fix (increasing `awake_duration`).

### Gremlin breakage 2: out-of-order desired delivery within a wake window
A subtle failure mode: if a device treats desired messages as **"last write wins" during a wake window**, then out-of-order delivery can cause it to miss the newest version.

Fix: during the wake window, keep the **maximum `v` observed** (or otherwise compare versions) before applying.

The simulator includes a `--naive-last-write` switch to reproduce this bug mode.

## Artifacts
- Protocol spec: `PROTOCOL.md`
- Simulator: `code/mqttsim/`
- CLI entrypoint: `code/run_sim.py`
- Tests: `tests/test_invariants.py`
- Run outputs: `results/runs/<run-name>/`
