from __future__ import annotations

import json
import struct
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


Event = dict[str, Any]
Subscriber = Callable[[str, dict[str, Any], bool, int], None]


@dataclass
class Broker:
    """Minimal in-process MQTT-like broker with retained-message support."""

    retained: dict[str, dict[str, Any]] = field(default_factory=dict)
    subscribers: dict[str, list[Subscriber]] = field(default_factory=dict)

    def subscribe(self, topic: str, callback: Subscriber, now: int) -> None:
        callbacks = self.subscribers.setdefault(topic, [])
        callbacks.append(callback)
        retained_payload = self.retained.get(topic)
        if retained_payload is not None:
            callback(topic, retained_payload, True, now)

    def unsubscribe(self, topic: str, callback: Subscriber) -> None:
        callbacks = self.subscribers.get(topic, [])
        if callback in callbacks:
            callbacks.remove(callback)

    def publish(self, topic: str, payload: dict[str, Any], retain: bool, now: int) -> None:
        if retain:
            self.retained[topic] = payload
        for callback in self.subscribers.get(topic, []):
            callback(topic, payload, retain, now)


@dataclass
class Device:
    """A sleepy device that wakes periodically and converges to desired state."""

    device_id: str
    wake_interval: int
    broker: Broker
    publish_hello: bool = False
    applied_v: int = 0
    pending_desired: dict[str, Any] | None = None
    apply_history: list[tuple[int, int]] = field(default_factory=list)

    def desired_topic(self) -> str:
        return f"dev/{self.device_id}/desired"

    def telemetry_topic(self) -> str:
        return f"dev/{self.device_id}/telemetry"

    def hello_topic(self) -> str:
        return f"dev/{self.device_id}/hello"

    def _on_desired(self, _topic: str, payload: dict[str, Any], _retained: bool, _ts: int) -> None:
        self.pending_desired = payload

    def wake(self, ts: int, events: list[Event]) -> None:
        self.broker.subscribe(self.desired_topic(), self._on_desired, ts)

        if self.publish_hello:
            hello = {"device_id": self.device_id, "ts": ts}
            self.broker.publish(self.hello_topic(), hello, retain=False, now=ts)
            events.append({"ts": ts, "kind": "hello", "topic": self.hello_topic(), "payload": hello})

        changed = False
        desired_v = self.applied_v
        if self.pending_desired:
            desired_v = int(self.pending_desired.get("v", self.applied_v))
            if desired_v > self.applied_v:
                self.applied_v = desired_v
                changed = True
                self.apply_history.append((ts, self.applied_v))
                events.append(
                    {
                        "ts": ts,
                        "kind": "apply",
                        "device_id": self.device_id,
                        "applied_v": self.applied_v,
                        "desired_v": desired_v,
                    }
                )

        telemetry = {
            "device_id": self.device_id,
            "ts": ts,
            "applied_v": self.applied_v,
            "desired_v": desired_v,
            "converged": self.applied_v == desired_v,
            "changed": changed,
        }
        self.broker.publish(self.telemetry_topic(), telemetry, retain=False, now=ts)
        events.append({"ts": ts, "kind": "telemetry", "topic": self.telemetry_topic(), "payload": telemetry})

        self.broker.unsubscribe(self.desired_topic(), self._on_desired)


@dataclass
class SimulationConfig:
    num_devices: int = 5
    wake_interval_base: int = 3
    wake_interval_step: int = 2
    duration: int = 60
    desired_updates: int = 4
    desired_update_period: int = 10
    publish_hello: bool = True


class Simulation:
    """Deterministic simulation of retained desired-state updates and sleepy devices."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.broker = Broker()
        self.events: list[Event] = []
        self.devices = [
            Device(
                device_id=f"d{i+1}",
                wake_interval=config.wake_interval_base + i * config.wake_interval_step,
                broker=self.broker,
                publish_hello=config.publish_hello,
            )
            for i in range(config.num_devices)
        ]
        self.final_desired_v = 0

    def _publish_desired(self, device_id: str, v: int, ts: int) -> None:
        payload = {"device_id": device_id, "v": v, "ts": ts}
        topic = f"dev/{device_id}/desired"
        self.broker.publish(topic, payload, retain=True, now=ts)
        self.events.append({"ts": ts, "kind": "desired", "topic": topic, "payload": payload, "retained": True})

    def run(self) -> dict[str, Any]:
        update_schedule: dict[int, int] = {}
        for idx in range(self.config.desired_updates):
            ts = idx * self.config.desired_update_period
            update_schedule[ts] = idx + 1

        for ts in range(self.config.duration + 1):
            if ts in update_schedule:
                version = update_schedule[ts]
                self.final_desired_v = version
                for dev in self.devices:
                    self._publish_desired(dev.device_id, version, ts)

            for dev in self.devices:
                if ts % dev.wake_interval == 0:
                    self.events.append({"ts": ts, "kind": "wake", "device_id": dev.device_id, "wake_interval": dev.wake_interval})
                    dev.wake(ts, self.events)

        monotonic = True
        convergence = True
        per_device = {}

        for dev in self.devices:
            history_versions = [v for _, v in dev.apply_history]
            if any(history_versions[i] > history_versions[i + 1] for i in range(len(history_versions) - 1)):
                monotonic = False

            converged = dev.applied_v == self.final_desired_v
            convergence = convergence and converged
            per_device[dev.device_id] = {
                "wake_interval": dev.wake_interval,
                "applied_v": dev.applied_v,
                "converged": converged,
                "applies": len(dev.apply_history),
            }

        summary = {
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": self.config.__dict__,
            "final_desired_v": self.final_desired_v,
            "monotonic_applied_v": monotonic,
            "converged": convergence,
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
            desired_v.append(int(event["payload"]["v"]))
        elif event["kind"] == "telemetry":
            payload = event["payload"]
            device_id = str(payload["device_id"])
            ts_vals, v_vals = device_series.setdefault(device_id, ([], []))
            ts_vals.append(int(payload["ts"]))
            v_vals.append(int(payload["applied_v"]))

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
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

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
    if plot_name:
        summary["plot"] = plot_name
    else:
        summary["plot"] = None
        summary["plot_note"] = "matplotlib unavailable; skipped PNG plot"

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
