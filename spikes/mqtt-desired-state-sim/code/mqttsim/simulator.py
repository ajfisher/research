from __future__ import annotations

import heapq
import json
import random
import struct
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


Event = dict[str, Any]
Subscriber = Callable[[str, dict[str, Any], bool, int], None]


def packed_version(epoch: int, v: int, scale: int = 1_000_000) -> int:
    """Combine (epoch, v) into a single monotonic integer if epoch never decreases."""

    return int(epoch) * scale + int(v)


@dataclass
class NetworkModel:
    """A tiny network model for message loss + delay + duplicates.

    - loss_rate is applied per-delivery (subscriber callback invocation).
    - delay is an integer number of simulation ticks.
    - dup_rate may schedule an additional duplicate delivery.

    This is intentionally simple; the goal is to stress protocol logic.
    """

    seed: int = 1
    loss_rate: float = 0.0
    min_delay: int = 0
    max_delay: int = 0
    dup_rate: float = 0.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.loss_rate <= 1.0):
            raise ValueError("loss_rate must be in [0,1]")
        if not (0.0 <= self.dup_rate <= 1.0):
            raise ValueError("dup_rate must be in [0,1]")
        if self.min_delay < 0 or self.max_delay < 0 or self.max_delay < self.min_delay:
            raise ValueError("invalid delay bounds")
        self._rng = random.Random(self.seed)

    def drop(self) -> bool:
        return self._rng.random() < self.loss_rate

    def delay(self) -> int:
        if self.max_delay == self.min_delay:
            return self.min_delay
        return self._rng.randint(self.min_delay, self.max_delay)


@dataclass
class Broker:
    """Minimal in-process MQTT-like broker with retained-message support.

    Adds a simple network model: each publish schedules per-subscriber deliveries
    that can be delayed or dropped.
    """

    network: NetworkModel = field(default_factory=NetworkModel)
    retained: dict[str, dict[str, Any]] = field(default_factory=dict)
    subscribers: dict[str, list[Subscriber]] = field(default_factory=dict)

    _queue: list[tuple[int, int, str, dict[str, Any], bool, Subscriber]] = field(default_factory=list, init=False)
    _seq: int = field(default=0, init=False)

    def reset_sessions(self) -> None:
        """Simulate a broker/controller restart: clears live sessions/in-flight messages.

        Retained messages remain.
        """

        self.subscribers.clear()
        self._queue.clear()

    def subscribe(self, topic: str, callback: Subscriber, now: int) -> None:
        callbacks = self.subscribers.setdefault(topic, [])
        callbacks.append(callback)
        retained_payload = self.retained.get(topic)
        if retained_payload is not None:
            # Retained replay is still subject to network delay/loss.
            self._schedule_delivery(topic, retained_payload, True, now, callback)

    def unsubscribe(self, topic: str, callback: Subscriber) -> None:
        callbacks = self.subscribers.get(topic, [])
        if callback in callbacks:
            callbacks.remove(callback)

    def publish(self, topic: str, payload: dict[str, Any], retain: bool, now: int) -> None:
        if retain:
            self.retained[topic] = payload
        for callback in list(self.subscribers.get(topic, [])):
            self._schedule_delivery(topic, payload, retain, now, callback)

    def _schedule_delivery(self, topic: str, payload: dict[str, Any], retain: bool, now: int, callback: Subscriber) -> None:
        if self.network.drop():
            return

        def push(deliver_at: int) -> None:
            self._seq += 1
            heapq.heappush(self._queue, (deliver_at, self._seq, topic, payload, retain, callback))

        deliver_at = now + self.network.delay()
        push(deliver_at)

        # Optional duplicates (idempotence stress)
        if self.network._rng.random() < self.network.dup_rate:
            push(deliver_at + self.network.delay())

    def tick(self, now: int) -> None:
        """Deliver all queued messages due at or before `now`."""

        while self._queue and self._queue[0][0] <= now:
            _deliver_at, _seq, topic, payload, retain, callback = heapq.heappop(self._queue)
            callback(topic, payload, retain, now)


@dataclass
class Device:
    """A sleepy device that wakes periodically and converges to desired state."""

    device_id: str
    wake_interval: int
    awake_duration: int
    broker: Broker
    publish_hello: bool = False
    naive_last_write: bool = False

    applied_ver: int = 0
    pending_desired: dict[str, Any] | None = None
    max_desired_ver_seen: int | None = None
    apply_history: list[tuple[int, int]] = field(default_factory=list)  # (ts, applied_ver)

    awake_until: int | None = None

    def desired_topic(self) -> str:
        return f"dev/{self.device_id}/desired"

    def telemetry_topic(self) -> str:
        return f"dev/{self.device_id}/telemetry"

    def hello_topic(self) -> str:
        return f"dev/{self.device_id}/hello"

    def _on_desired(self, _topic: str, payload: dict[str, Any], _retained: bool, _ts: int) -> None:
        # Gremlin scenario: out-of-order delivery can mean an older desired arrives after a newer
        # one. If we naively take "last write", we can miss the newest version.
        if self.naive_last_write:
            self.pending_desired = payload
            return

        epoch = int(payload.get("epoch", 0))
        v = int(payload.get("v", 0))
        ver = packed_version(epoch, v)
        if self.max_desired_ver_seen is None or ver > self.max_desired_ver_seen:
            self.max_desired_ver_seen = ver
            self.pending_desired = payload

    def wake_start(self, ts: int, events: list[Event]) -> None:
        self.awake_until = ts + max(1, self.awake_duration) - 1
        self.pending_desired = None
        self.max_desired_ver_seen = None

        self.broker.subscribe(self.desired_topic(), self._on_desired, ts)
        events.append({"ts": ts, "kind": "wake", "device_id": self.device_id, "wake_interval": self.wake_interval, "awake_duration": self.awake_duration})

        if self.publish_hello:
            hello = {"device_id": self.device_id, "ts": ts}
            self.broker.publish(self.hello_topic(), hello, retain=False, now=ts)
            events.append({"ts": ts, "kind": "hello", "topic": self.hello_topic(), "payload": hello})

    def is_awake(self, ts: int) -> bool:
        return self.awake_until is not None and ts <= self.awake_until

    def wake_end(self, ts: int, events: list[Event]) -> None:
        # Apply desired at the end of the wake window (one-shot apply).
        changed = False
        desired_epoch = 0
        desired_v = 0
        desired_ver = self.applied_ver
        if self.pending_desired:
            desired_epoch = int(self.pending_desired.get("epoch", 0))
            desired_v = int(self.pending_desired.get("v", 0))
            desired_ver = packed_version(desired_epoch, desired_v)
            if desired_ver > self.applied_ver:
                self.applied_ver = desired_ver
                changed = True
                self.apply_history.append((ts, self.applied_ver))
                events.append(
                    {
                        "ts": ts,
                        "kind": "apply",
                        "device_id": self.device_id,
                        "applied_ver": self.applied_ver,
                        "desired_ver": desired_ver,
                        "epoch": desired_epoch,
                        "v": desired_v,
                    }
                )

        telemetry = {
            "device_id": self.device_id,
            "ts": ts,
            "applied_ver": self.applied_ver,
            "desired_ver": desired_ver,
            "epoch": desired_epoch,
            "v": desired_v,
            "converged": self.applied_ver == desired_ver,
            "changed": changed,
        }
        self.broker.publish(self.telemetry_topic(), telemetry, retain=False, now=ts)
        events.append({"ts": ts, "kind": "telemetry", "topic": self.telemetry_topic(), "payload": telemetry})

        self.broker.unsubscribe(self.desired_topic(), self._on_desired)
        self.awake_until = None


@dataclass
class SimulationConfig:
    num_devices: int = 5
    wake_interval_base: int = 3
    wake_interval_step: int = 2
    awake_duration: int = 1
    duration: int = 60
    desired_updates: int = 4
    desired_update_period: int = 10
    publish_hello: bool = True

    # network stressors
    seed: int = 1
    loss_rate: float = 0.0
    min_delay: int = 0
    max_delay: int = 0
    dup_rate: float = 0.0

    # protocol behavior toggles
    naive_last_write: bool = False

    # control-plane / epoch behavior
    controller_epoch_start: int = 1
    controller_epoch_reset_at: int | None = None
    controller_epoch_reset_mode: str = "increment"  # increment|reset0 (bug)
    republish_on_hello: bool = False

    # optional breakage lever
    broker_restart_at: int | None = None


class ControlPlane:
    """Publishes desired state updates and optionally republish-on-hello (state pull)."""

    def __init__(self, broker: Broker, device_ids: list[str], epoch_start: int, republish_on_hello: bool, events: list[Event]):
        self.broker = broker
        self.device_ids = device_ids
        self.epoch = int(epoch_start)
        self.v = 0
        self.events = events
        self.republish_on_hello = republish_on_hello
        if self.republish_on_hello:
            for device_id in self.device_ids:
                self.broker.subscribe(f"dev/{device_id}/hello", self._on_hello, now=0)

    def reset_epoch(self, mode: str, ts: int) -> None:
        if mode == "increment":
            self.epoch += 1
        elif mode == "reset0":
            self.epoch = 0
        else:
            raise ValueError(f"unknown controller_epoch_reset_mode: {mode}")
        self.v = 0
        self.events.append({"ts": ts, "kind": "controller_epoch_reset", "epoch": self.epoch, "mode": mode})

    def publish_update(self, ts: int) -> None:
        self.v += 1
        for device_id in self.device_ids:
            self._publish_desired(device_id, ts)

    def _publish_desired(self, device_id: str, ts: int) -> None:
        payload = {"device_id": device_id, "epoch": self.epoch, "v": self.v, "ts": ts, "ver": packed_version(self.epoch, self.v)}
        topic = f"dev/{device_id}/desired"
        self.broker.publish(topic, payload, retain=True, now=ts)
        self.events.append({"ts": ts, "kind": "desired", "topic": topic, "payload": payload, "retained": True})

    def _on_hello(self, topic: str, payload: dict[str, Any], _retained: bool, ts: int) -> None:
        # device_id from topic: dev/<id>/hello
        parts = topic.split("/")
        device_id = parts[1] if len(parts) > 1 else payload.get("device_id", "")
        self.events.append({"ts": ts, "kind": "controller_seen_hello", "device_id": device_id})
        if device_id:
            self._publish_desired(device_id, ts)


class Simulation:
    """Deterministic simulation of retained desired-state updates and sleepy devices."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.broker = Broker(
            network=NetworkModel(
                seed=config.seed,
                loss_rate=config.loss_rate,
                min_delay=config.min_delay,
                max_delay=config.max_delay,
                dup_rate=config.dup_rate,
            )
        )
        self.events: list[Event] = []
        self.devices = [
            Device(
                device_id=f"d{i+1}",
                wake_interval=config.wake_interval_base + i * config.wake_interval_step,
                awake_duration=config.awake_duration,
                broker=self.broker,
                publish_hello=config.publish_hello,
                naive_last_write=config.naive_last_write,
            )
            for i in range(config.num_devices)
        ]
        self.control = ControlPlane(
            broker=self.broker,
            device_ids=[d.device_id for d in self.devices],
            epoch_start=config.controller_epoch_start,
            republish_on_hello=config.republish_on_hello,
            events=self.events,
        )
        self.final_desired_ver = 0

    def run(self) -> dict[str, Any]:
        update_schedule = {idx * self.config.desired_update_period: True for idx in range(self.config.desired_updates)}

        for ts in range(self.config.duration + 1):
            if self.config.broker_restart_at is not None and ts == self.config.broker_restart_at:
                self.events.append({"ts": ts, "kind": "broker_restart"})
                self.broker.reset_sessions()
                # If republish-on-hello is enabled, the controller needs to resubscribe to hello topics.
                if self.config.republish_on_hello:
                    self.control = ControlPlane(
                        broker=self.broker,
                        device_ids=[d.device_id for d in self.devices],
                        epoch_start=self.control.epoch,
                        republish_on_hello=True,
                        events=self.events,
                    )

            if self.config.controller_epoch_reset_at is not None and ts == self.config.controller_epoch_reset_at:
                self.control.reset_epoch(self.config.controller_epoch_reset_mode, ts)

            if ts in update_schedule:
                self.control.publish_update(ts)
                self.final_desired_ver = packed_version(self.control.epoch, self.control.v)

            # Start wake windows
            for dev in self.devices:
                if dev.awake_until is None and ts % dev.wake_interval == 0:
                    dev.wake_start(ts, self.events)

            # Deliver due network messages
            self.broker.tick(ts)

            # End wake windows
            for dev in self.devices:
                if dev.awake_until is not None and ts == dev.awake_until:
                    dev.wake_end(ts, self.events)

        # Drain any remaining messages (mainly for completeness)
        self.broker.tick(self.config.duration + self.config.max_delay + 1)

        monotonic = True
        convergence = True
        per_device: dict[str, Any] = {}

        for dev in self.devices:
            history_versions = [v for _, v in dev.apply_history]
            if any(history_versions[i] > history_versions[i + 1] for i in range(len(history_versions) - 1)):
                monotonic = False

            converged = dev.applied_ver == self.final_desired_ver
            convergence = convergence and converged
            per_device[dev.device_id] = {
                "wake_interval": dev.wake_interval,
                "awake_duration": dev.awake_duration,
                "applied_ver": dev.applied_ver,
                "converged": converged,
                "applies": len(dev.apply_history),
            }

        stale_count = sum(1 for d in per_device.values() if not d["converged"])

        summary = {
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": self.config.__dict__,
            "final_desired": {"epoch": self.control.epoch, "v": self.control.v, "ver": self.final_desired_ver},
            "monotonic_applied_ver": monotonic,
            "converged": convergence,
            "stale_device_count": stale_count,
            "devices": per_device,
            "event_count": len(self.events),
        }
        return summary


def maybe_plot(events: list[Event], out_dir: Path) -> str | None:
    """Create a PNG plot (matplotlib preferred, pure-Python fallback)."""
    desired_ts: list[int] = []
    desired_v: list[int] = []
    device_series: dict[str, tuple[list[int], list[int]]] = {}

    for event in events:
        if event["kind"] == "desired":
            desired_ts.append(int(event["ts"]))
            desired_v.append(int(event["payload"].get("ver", packed_version(int(event["payload"].get("epoch", 0)), int(event["payload"].get("v", 0))))) )
        elif event["kind"] == "telemetry":
            payload = event["payload"]
            device_id = str(payload["device_id"])
            ts_vals, v_vals = device_series.setdefault(device_id, ([], []))
            ts_vals.append(int(payload["ts"]))
            v_vals.append(int(payload.get("applied_ver", 0)))

    try:
        import matplotlib.pyplot as plt  # type: ignore

        fig, ax = plt.subplots(figsize=(10, 6))
        if desired_ts:
            ax.step(desired_ts, desired_v, where="post", label="desired_v", linewidth=2)

        for device_id, (ts_vals, v_vals) in sorted(device_series.items()):
            ax.plot(ts_vals, v_vals, marker="o", linestyle="-", alpha=0.8, label=f"{device_id} applied_v")

        ax.set_title("Desired vs Applied Versions")
        ax.set_xlabel("time step")
        ax.set_ylabel("version")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()

        plot_path = out_dir / "applied_versions.png"
        fig.savefig(plot_path)
        plt.close(fig)
        return plot_path.name
    except Exception:
        return _fallback_plot_png(out_dir / "applied_versions.png", desired_ts, desired_v, device_series)


def _fallback_plot_png(
    plot_path: Path,
    desired_ts: list[int],
    desired_v: list[int],
    device_series: dict[str, tuple[list[int], list[int]]],
) -> str:
    width = 960
    height = 540
    margin_left = 60
    margin_right = 30
    margin_top = 30
    margin_bottom = 40

    # RGB image buffer
    pixels = bytearray([245, 246, 248] * width * height)

    def set_px(x: int, y: int, r: int, g: int, b: int) -> None:
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            pixels[idx] = r
            pixels[idx + 1] = g
            pixels[idx + 2] = b

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int], thickness: int = 1) -> None:
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for tx in range(-(thickness // 2), thickness // 2 + 1):
                for ty in range(-(thickness // 2), thickness // 2 + 1):
                    set_px(x0 + tx, y0 + ty, color[0], color[1], color[2])
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    all_ts: list[int] = desired_ts[:]
    all_vs: list[int] = desired_v[:]
    for ts_vals, v_vals in device_series.values():
        all_ts.extend(ts_vals)
        all_vs.extend(v_vals)

    min_ts = min(all_ts) if all_ts else 0
    max_ts = max(all_ts) if all_ts else 1
    min_v = min(all_vs) if all_vs else 0
    max_v = max(all_vs) if all_vs else 1
    if max_ts == min_ts:
        max_ts += 1
    if max_v == min_v:
        max_v += 1

    x0 = margin_left
    y0 = height - margin_bottom
    x1 = width - margin_right
    y1 = margin_top

    # Axes
    line(x0, y0, x1, y0, (70, 70, 80), thickness=2)
    line(x0, y0, x0, y1, (70, 70, 80), thickness=2)

    def sx(ts: int) -> int:
        return int(x0 + (ts - min_ts) * (x1 - x0) / (max_ts - min_ts))

    def sy(v: int) -> int:
        return int(y0 - (v - min_v) * (y0 - y1) / (max_v - min_v))

    palette = [
        (31, 119, 180),
        (255, 127, 14),
        (44, 160, 44),
        (214, 39, 40),
        (148, 103, 189),
        (140, 86, 75),
    ]

    # Desired line (step approximation)
    if desired_ts and desired_v:
        for i in range(len(desired_ts) - 1):
            line(sx(desired_ts[i]), sy(desired_v[i]), sx(desired_ts[i + 1]), sy(desired_v[i]), (20, 20, 20), thickness=2)
            line(sx(desired_ts[i + 1]), sy(desired_v[i]), sx(desired_ts[i + 1]), sy(desired_v[i + 1]), (20, 20, 20), thickness=2)

    # Device lines
    for idx, (_device_id, (ts_vals, v_vals)) in enumerate(sorted(device_series.items())):
        color = palette[idx % len(palette)]
        for i in range(len(ts_vals) - 1):
            line(sx(ts_vals[i]), sy(v_vals[i]), sx(ts_vals[i + 1]), sy(v_vals[i + 1]), color, thickness=2)

    _write_png_rgb(plot_path, width, height, pixels)
    return plot_path.name


def _write_png_rgb(path: Path, width: int, height: int, rgb: bytes) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)
        ) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    row_bytes = width * 3
    for y in range(height):
        raw.append(0)  # filter type 0
        start = y * row_bytes
        raw.extend(rgb[start : start + row_bytes])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=9)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    path.write_bytes(png)


def write_outputs(out_dir: Path, events: list[Event], summary: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    events_path = out_dir / "events.ndjson"
    with events_path.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    summary_path = out_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")

    plot_name = maybe_plot(events, out_dir)
    summary["plot"] = plot_name

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
