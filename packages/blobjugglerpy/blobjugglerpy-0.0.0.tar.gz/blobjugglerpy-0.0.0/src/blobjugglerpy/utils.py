"""
General utilities for value normalization, sequences, time conversions, and math helpers.
"""

from __future__ import annotations

import math
import numbers
import array
from collections.abc import Sequence

try:  # Optional numpy normalization
    import numpy as np
except Exception:  # pragma: no cover - numpy is optional
    np = None


def quat_to_euler(w: float, x: float, y: float, z: float):
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)
    t2 = +2.0 * (w * y - z * x)
    t2 = max(min(t2, +1.0), -1.0)
    pitch = math.asin(t2)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)
    return roll, pitch, yaw


def time_to_float_seconds(value) -> float | None:
    try:
        sec = getattr(value, "sec", None)
        nsec = getattr(value, "nanosec", None)
        if sec is not None and nsec is not None:
            return float(sec) + float(nsec) * 1e-9
    except Exception:
        pass
    return None


def is_numeric_sequence(seq) -> bool:
    try:
        for x in seq:
            if isinstance(x, numbers.Real):
                continue
            if np is not None and isinstance(x, np.generic):
                continue
            return False
        return True
    except Exception:
        return False


def to_python_scalar(value):
    if np is not None:
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray) and value.ndim == 0:
            return value.item()
    return value


def sequence_to_list(obj):
    if isinstance(obj, (str, bytes, bytearray)):
        return None
    if isinstance(obj, (list, tuple)):
        return list(obj)
    if isinstance(obj, array.array):
        return obj.tolist()
    if np is not None and isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Sequence):
        try:
            return list(obj)
        except TypeError:
            return None
    return None


def is_float_like(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, float):
        return True
    if np is not None and isinstance(value, np.floating):
        return True
    return False


def format_csv_value(column: str, value):
    if value is None:
        return None
    if is_float_like(value):
        v = float(value)
        if column == "__time":
            return f"{v:.6f}"
        if column == "__header_time" or column.endswith("/stamp"):
            return f"{v:.9f}"
    return value


def int_sqrt(n: int) -> int | None:
    r = int(round(n ** 0.5))
    return r if r * r == n else None


def publish_time_sec(_msg, bag_time_ns: int) -> float:
    return float(bag_time_ns) * 1e-9


def header_time_sec(msg) -> float | None:
    if hasattr(msg, "header") and hasattr(msg.header, "stamp"):
        return time_to_float_seconds(msg.header.stamp)
    return None


__all__ = [
    "quat_to_euler",
    "time_to_float_seconds",
    "is_numeric_sequence",
    "to_python_scalar",
    "sequence_to_list",
    "is_float_like",
    "format_csv_value",
    "int_sqrt",
    "publish_time_sec",
    "header_time_sec",
]
