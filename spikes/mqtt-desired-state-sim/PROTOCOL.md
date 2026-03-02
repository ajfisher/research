# MQTT Desired-State Protocol Simulator (Sleepy Devices)

## Goal
Model a device-agnostic desired-state pattern for intermittently connected (sleepy) devices.

## Topic Contract
- `dev/<id>/desired`
  - Retained: **yes**
  - Publisher: control plane
  - Consumer: device
  - Payload (JSON): `{ "device_id": "d1", "v": 3, "ts": 20 }`
  - Semantics: last-write-wins desired version `v` for each device.

- `dev/<id>/telemetry`
  - Retained: **no**
  - Publisher: device
  - Consumer: observer/control plane
  - Payload (JSON): `{ "device_id": "d1", "ts": 21, "applied_v": 3, "desired_v": 3, "converged": true, "changed": false }`
  - Semantics: emitted on wake to report current applied state.

- `dev/<id>/hello` (optional)
  - Retained: **no**
  - Publisher: device
  - Payload (JSON): `{ "device_id": "d1", "ts": 21 }`
  - Semantics: lightweight online pulse when the device wakes.

## Sleepy Device Behavior
1. Device wakes on interval.
2. Device subscribes to `dev/<id>/desired`.
3. Broker immediately delivers retained desired payload if present.
4. Device applies desired state only if `desired.v > applied_v`.
5. Device publishes telemetry (and optional hello).
6. Device disconnects/sleeps.

## Invariants
- Applied versions per device are monotonic non-decreasing.
- If simulation duration is long enough relative to wake intervals, all devices converge to latest retained desired version.

## Notes
- No hardware mapping (including Inkplate) is included.
- This simulator is in-process and does not implement full MQTT QoS/session semantics.
