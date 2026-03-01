# MQTT Desired-State Protocol Simulator (Sleepy Devices)

## Objective
Explore a device-agnostic retained desired-state protocol for sleepy/periodically-connected devices.

## Background
Sleepy devices may miss live publishes while offline. Retained desired-state topics solve this by replaying latest intent at reconnect/wake.

## Methodology
- Implemented an in-process MQTT-like broker with retained messages.
- Simulated control-plane desired updates and sleepy device wake cycles.
- Recorded event-level traces and run summaries.
- Verified core invariants with unit tests.

## Setup
Python 3.10+ is sufficient. No mandatory dependencies.

Optional plotting dependency for higher-quality plots:
```bash
pip install matplotlib
```

## Usage
Run a simulation:

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --num-devices 6 \
  --duration 90 \
  --desired-updates 5 \
  --desired-update-period 12
```

Use explicit run name/output root:

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name baseline-01 \
  --out-root spikes/mqtt-desired-state-sim/results/runs
```

Disable optional hello topic:

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py --disable-hello
```

Run tests:

```bash
python -m unittest discover -s spikes/mqtt-desired-state-sim/tests -p 'test_*.py'
```

## Results
Each run writes to:

```text
spikes/mqtt-desired-state-sim/results/runs/<run-name>/
  events.ndjson
  summary.json
  applied_versions.png   # always generated (matplotlib or pure-Python fallback)
```

- `events.ndjson`: ordered event log (`desired`, `wake`, `hello`, `apply`, `telemetry`)
- `summary.json`: config, convergence, monotonicity, per-device outcomes

## Conclusions
A retained `dev/<id>/desired` topic with non-retained telemetry is enough to model deterministic convergence for sleepy devices in this simplified setting.

## Future Work
- Add wildcard subscriptions and multiple observers.
- Add message loss and delay models.
- Add richer desired payload conflict semantics (version vectors/epochs).
