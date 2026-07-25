"""Lightweight Lua behavior simulator for legacy comparison tests.

The original Lua runtime is not embedded in this Python project. This module
provides deterministic parsing/calculation helpers that mimic the data shape
expected by historical test suites.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _to_seconds(h: int, m: int, s: int) -> int:
    return h * 3600 + m * 60 + s


def _pretty_time(seconds: int) -> str:
    seconds = seconds % 86400
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


@dataclass
class LuaAction:
    action: str
    time_start: Optional[int]
    time_end: Optional[int]
    interval: Optional[float]
    aperture: Optional[float]
    iso: Optional[int]
    shutter_speed: Optional[float]
    mlu_delay: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "interval": self.interval,
            "aperture": self.aperture,
            "iso": self.iso,
            "shutter_speed": self.shutter_speed,
            "mlu_delay": self.mlu_delay,
        }


class LuaSimulator:
    """Compatibility simulator for tests expecting a Lua execution API."""

    def __init__(self, config_file: str):
        self.config_file = config_file

    def convert_second(self, hrs: int, mins: int, secs: int) -> int:
        return _to_seconds(hrs, mins, secs)

    def pretty_time(self, seconds: int) -> str:
        return _pretty_time(seconds)

    def convert_time(self, reference: str, operation: str, time_in: int, table_ref: List[int]) -> int:
        idx = {"C1": 0, "C2": 1, "Max": 2, "C3": 3, "C4": 4}.get(reference)
        if idx is None:
            raise ValueError(f"Invalid reference: {reference}")

        base = table_ref[idx]
        if operation == "+":
            out = base + time_in
        elif operation == "-":
            out = base - time_in
        else:
            raise ValueError(f"Invalid operation: {operation}")
        return out % 86400

    def run(self, start_time_hms: Tuple[int, int, int] | None = None) -> Dict[str, Any]:
        return run_lua_simulation(self.config_file, start_time_hms=start_time_hms)


def _parse_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _seconds_from_hms_fields(fields: List[str], start_idx: int) -> int:
    return _to_seconds(_parse_int(fields[start_idx]), _parse_int(fields[start_idx + 1]), _parse_int(fields[start_idx + 2]))


def _resolve_relative_time(ref_times: Dict[str, int], ref: str, op: str, offset_seconds: int) -> Optional[int]:
    if ref == "-":
        return offset_seconds
    if ref not in ref_times:
        return None
    if op == "+":
        return (ref_times[ref] + offset_seconds) % 86400
    return (ref_times[ref] - offset_seconds) % 86400


def run_lua_simulation(config_file: str, start_time_hms: Tuple[int, int, int] | None = None) -> Dict[str, Any]:
    """Parse a legacy SOLARECL-like config and return Lua-shaped results."""

    path = Path(config_file)
    if not path.exists():
        return {
            "error": f"File not found: {config_file}",
            "config": {},
            "actions_executed": [],
            "logs": ["Script loading failed", "Normal exit"],
        }

    ref_times: Dict[str, int] = {}
    test_mode = 0
    actions: List[LuaAction] = []
    logs: List[str] = ["Script loading", "Configuration parsing"]

    try:
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue

                fields = [p.strip() for p in line.split(",")]
                if not fields:
                    continue

                kind = fields[0]

                if kind == "Config" and len(fields) >= 17:
                    ref_times = {
                        "C1": _seconds_from_hms_fields(fields, 1),
                        "C2": _seconds_from_hms_fields(fields, 4),
                        "Max": _seconds_from_hms_fields(fields, 7),
                        "C3": _seconds_from_hms_fields(fields, 10),
                        "C4": _seconds_from_hms_fields(fields, 13),
                    }
                    test_mode = _parse_int(fields[16], default=0)
                    continue

                if kind not in {"Photo", "Boucle", "Interval"}:
                    continue

                if kind == "Photo" and len(fields) >= 13:
                    offset = _seconds_from_hms_fields(fields, 3)
                    time_start = _resolve_relative_time(ref_times, fields[1], fields[2], offset)
                    camera_idx = 12 if len(fields) >= 16 else 9
                    actions.append(
                        LuaAction(
                            action="Photo",
                            time_start=time_start,
                            time_end=None,
                            interval=None,
                            aperture=_parse_float(fields[camera_idx], default=0.0),
                            iso=_parse_int(fields[camera_idx + 1], default=0),
                            shutter_speed=_parse_float(fields[camera_idx + 2], default=0.0),
                            mlu_delay=_parse_int(fields[camera_idx + 3], default=0),
                        )
                    )
                    continue

                if kind in {"Boucle", "Interval"} and len(fields) >= 15:
                    start_offset = _seconds_from_hms_fields(fields, 3)
                    if fields[6] in {"C1", "C2", "Max", "C3", "C4", "-"}:
                        end_ref = fields[6]
                        end_op = fields[7]
                        end_offset = _seconds_from_hms_fields(fields, 8)
                        interval_idx = 11
                        camera_idx = 12
                    else:
                        end_ref = fields[1]
                        end_op = fields[6]
                        end_offset = _seconds_from_hms_fields(fields, 7)
                        interval_idx = 10
                        camera_idx = 11

                    time_start = _resolve_relative_time(ref_times, fields[1], fields[2], start_offset)
                    time_end = _resolve_relative_time(ref_times, end_ref, end_op, end_offset)

                    interval_value = _parse_float(fields[interval_idx], default=0.0)
                    if kind == "Interval" and time_start is not None and time_end is not None and interval_value > 0:
                        interval_value = float(time_end - time_start) / float(interval_value)

                    actions.append(
                        LuaAction(
                            action=kind,
                            time_start=time_start,
                            time_end=time_end,
                            interval=interval_value,
                            aperture=_parse_float(fields[camera_idx], default=0.0),
                            iso=_parse_int(fields[camera_idx + 1], default=0),
                            shutter_speed=_parse_float(fields[camera_idx + 2], default=0.0),
                            mlu_delay=_parse_int(fields[camera_idx + 3], default=0),
                        )
                    )

        logs.append("Normal exit")
        if start_time_hms is not None:
            logs.append(f"Start time: {_pretty_time(_to_seconds(*start_time_hms))}")

        return {
            "config": {
                "C1": ref_times.get("C1"),
                "C2": ref_times.get("C2"),
                "Max": ref_times.get("Max"),
                "C3": ref_times.get("C3"),
                "C4": ref_times.get("C4"),
                "TestMode": test_mode,
            },
            "actions_executed": [a.as_dict() for a in actions],
            "logs": logs,
        }

    except Exception as exc:
        return {
            "error": str(exc),
            "config": {},
            "actions_executed": [],
            "logs": ["Script loading", f"Error: {exc}", "Normal exit"],
        }
