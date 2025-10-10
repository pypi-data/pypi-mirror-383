"""Minimal opt-in telemetry for Flow CLI.

Writes JSONL events to ~/.flow/metrics.jsonl when FLOW_TELEMETRY=1.
Never raises; best-effort only.

When enabled and an Amplitude key is set, events are also mirrored to
Amplitude via ``flow.utils.analytics``.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CommandMetric:
    command: str
    duration: float
    success: bool
    error_type: str | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class Telemetry:
    def __init__(self) -> None:
        try:
            from flow.utils import analytics as _analytics

            self.enabled = bool(_analytics.telemetry_enabled())
        except Exception:  # noqa: BLE001
            self.enabled = os.environ.get("FLOW_TELEMETRY", "0") == "1"
        self.metrics_file = Path.home() / ".flow" / "metrics.jsonl"
        self._lock = threading.Lock()

    def track_command(self, command: str) -> object:
        class CommandTracker:
            def __init__(self, telemetry: Telemetry, command: str) -> None:
                self.telemetry = telemetry
                self.command = command
                self.start_time: float | None = None

            def __enter__(self) -> CommandTracker:
                self.start_time = time.time()
                return self

            def __exit__(
                self,
                exc_type: type[BaseException] | None,
                exc_val: BaseException | None,
                exc_tb: Any,
            ) -> None:
                if not self.telemetry.enabled:
                    return
                try:
                    duration = 0.0
                    if self.start_time is not None:
                        duration = time.time() - self.start_time
                    success = exc_type is None
                    err_name = None
                    try:
                        import click as _click  # local import

                        if exc_type is _click.exceptions.Exit and hasattr(exc_val, "exit_code"):
                            code = getattr(exc_val, "exit_code", 1)
                            success = code == 0
                            err_name = None if success else "Exit"
                        else:
                            err_name = exc_type.__name__ if exc_type else None
                    except Exception:  # noqa: BLE001
                        err_name = exc_type.__name__ if exc_type else None

                    # Prefer full command path when available (e.g., "ssh-keys add")
                    try:
                        import click as _click  # local import

                        ctx = _click.get_current_context(silent=True)
                        full_name = (
                            ctx.command_path
                            if ctx and getattr(ctx, "command_path", None)
                            else self.command
                        )
                    except Exception:  # noqa: BLE001
                        full_name = self.command

                    metric = CommandMetric(
                        command=full_name,
                        duration=duration,
                        success=bool(success),
                        error_type=err_name,
                    )
                    self.telemetry.write_metric(metric)
                    # Optional Amplitude sink (opt-in via FLOW_AMPLITUDE_API_KEY)
                    try:
                        from flow.utils import analytics as _analytics

                        _analytics.track(
                            "cli_command",
                            {
                                "command": full_name,
                                "success": bool(metric.success),
                                "error_type": metric.error_type or "",
                                "duration_ms": int(metric.duration * 1000),
                                "origin": "cli",
                            },
                        )
                    except Exception:  # noqa: BLE001
                        pass
                except Exception:  # noqa: BLE001
                    # Never raise from telemetry
                    pass

        return CommandTracker(self, command)

    def _write_metric(self, metric: CommandMetric) -> None:
        with self._lock:
            try:
                self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
                created = not self.metrics_file.exists()
                with open(self.metrics_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(asdict(metric)) + "\n")
                if created:
                    try:
                        if os.name == "posix":
                            os.chmod(self.metrics_file, 0o600)
                    except OSError:
                        pass
            except OSError:
                pass

    # Public API for writing a metric; used by nested trackers to avoid
    # cross-object access to a private method per repo lint policy
    def write_metric(self, metric: CommandMetric) -> None:
        self._write_metric(metric)

    def log_event(self, event: str, properties: dict[str, Any] | None = None) -> None:
        """Write an arbitrary event to the telemetry sink when enabled.

        This is a best-effort operation and will never raise.
        """
        if not self.enabled:
            return
        try:
            payload = asdict(EventMetric(event=event, properties=_safe_dict(properties)))
            with self._lock:
                try:
                    self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
                    created = not self.metrics_file.exists()
                    with open(self.metrics_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(payload) + "\n")
                    if created:
                        try:
                            if os.name == "posix":
                                os.chmod(self.metrics_file, 0o600)
                        except OSError:
                            pass
                except OSError:
                    pass
            # Optional Amplitude sink
            try:
                from flow.utils import analytics as _analytics

                _analytics.track(event, _safe_dict(properties))
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001
            pass


# --- Extended event logging (opt-in) ---


@dataclass
class EventMetric:
    event: str
    properties: dict[str, Any]
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


def _safe_dict(obj: dict[str, Any] | None) -> dict[str, Any]:
    try:
        if not obj:
            return {}
        # Ensure JSON-serializable by coercing values to basic types when needed
        result: dict[str, Any] = {}
        for k, v in obj.items():
            try:
                json.dumps({k: v})
                result[k] = v
            except Exception:  # noqa: BLE001
                result[k] = str(v)
        return result
    except Exception:  # noqa: BLE001
        return {}
