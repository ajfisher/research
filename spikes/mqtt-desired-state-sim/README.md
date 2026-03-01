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

## Gremlin scenarios (try to break it)

Lossy deliveries (retained intent + repeated wakes usually survives):

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name gremlin-loss \
  --seed 7 \
  --loss 0.3
```

Delayed deliveries with too-short awake window (fails to converge):

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name gremlin-delay-miss \
  --seed 3 \
  --min-delay 2 --max-delay 5 \
  --awake-duration 1
```

Fix: extend awake window to exceed max delay (converges again):

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name gremlin-delay-fixed \
  --seed 3 \
  --min-delay 2 --max-delay 5 \
  --awake-duration 6
```

### Out-of-order delivery within a wake window

If you (incorrectly) treat desired messages as "last write wins" during a wake window, out-of-order delivery can cause a device to **miss** the newest version.

Reproduce the bug:

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name evil-reorder-naive \
  --seed 1 \
  --num-devices 20 \
  --duration 200 \
  --min-delay 0 --max-delay 40 \
  --awake-duration 60 \
  --naive-last-write
```

Correct behavior (default): device keeps the max `v` seen during the wake window.

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name evil-reorder-fixed \
  --seed 1 \
  --num-devices 20 \
  --duration 200 \
  --min-delay 0 --max-delay 40 \
  --awake-duration 60
```

### Duplicates + loss

```bash
python spikes/mqtt-desired-state-sim/code/run_sim.py \
  --run-name evil-dup-loss \
  --seed 9 \
  --num-devices 20 \
  --duration 200 \
  --min-delay 0 --max-delay 40 \
  --awake-duration 60 \
  --loss 0.2 \
  --dup 0.5
```

Run tests:

```bash
python -m unittest discover -s spikes/mqtt-desired-state-sim/tests -p 'test_*.py'
```

## Scenario sweeps (retries + spread)

Run a bundle of gremlin scenarios multiple times and write aggregates:

```bash
python spikes/mqtt-desired-state-sim/code/run_scenarios.py --retries 20
```

Outputs:
- `spikes/mqtt-desired-state-sim/results/scenarios/<scenario>/rep-0000/...` (per-run artifacts)
- `spikes/mqtt-desired-state-sim/results/scenarios/<scenario>/aggregate.json` (spread metrics)

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
