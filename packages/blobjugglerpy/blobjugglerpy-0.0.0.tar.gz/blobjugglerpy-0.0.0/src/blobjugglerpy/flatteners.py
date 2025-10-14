"""
Message flattening utilities for PlotJuggler-style and generic per-topic CSVs.
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict

from .utils import (
    quat_to_euler,
    time_to_float_seconds,
    sequence_to_list,
    is_numeric_sequence,
    to_python_scalar,
    int_sqrt,
)


def flatten_plotjuggler(msg, topic: str) -> OrderedDict:
    base = "/" + topic.strip("/")
    out = OrderedDict()

    def rec(obj, path_parts):
        if hasattr(obj, "get_fields_and_field_types"):
            fields = list(obj.get_fields_and_field_types().keys())
            if set(fields) == set(["sec", "nanosec"]):
                key = base + "/" + "/".join(path_parts) if path_parts else base
                out[key] = time_to_float_seconds(obj)
                return
            for fname in fields:
                rec(getattr(obj, fname), path_parts + [fname])
            return

        seq = sequence_to_list(obj)
        if seq is not None:
            if len(seq) > 0 and is_numeric_sequence(seq):
                n = int_sqrt(len(seq))
                if n is not None and n >= 2:
                    for i in range(n):
                        for j in range(n):
                            idx = i * n + j
                            key = base + "/" + "/".join(path_parts) + "/[{};{}]".format(i, j)
                            out[key] = to_python_scalar(seq[idx]) if idx < len(seq) else None
                    return
            for i, elem in enumerate(seq):
                if path_parts:
                    segs = list(path_parts)
                    segs[-1] = "{}[{}]".format(segs[-1], i)
                    rec(elem, segs)
                else:
                    rec(elem, ["[{}]".format(i)])
            return

        key = base + "/" + "/".join(path_parts) if path_parts else base
        out[key] = to_python_scalar(obj)

    rec(msg, [])

    orientation_groups = {}
    for k in list(out.keys()):
        if k.endswith("/orientation/w"):
            base_key = k[: -len("/w")]
            orientation_groups.setdefault(base_key, {})["w"] = out[k]
        elif k.endswith("/orientation/x"):
            base_key = k[: -len("/x")]
            orientation_groups.setdefault(base_key, {})["x"] = out[k]
        elif k.endswith("/orientation/y"):
            base_key = k[: -len("/y")]
            orientation_groups.setdefault(base_key, {})["y"] = out[k]
        elif k.endswith("/orientation/z"):
            base_key = k[: -len("/z")]
            orientation_groups.setdefault(base_key, {})["z"] = out[k]

    for base_key, comps in orientation_groups.items():
        if all(c in comps for c in ("w", "x", "y", "z")):
            try:
                r, p, y = quat_to_euler(comps["w"], comps["x"], comps["y"], comps["z"])
                out[base_key + "/roll"] = r
                out[base_key + "/pitch"] = p
                out[base_key + "/yaw"] = y
            except Exception:
                pass

    return out


def flatten_field_generic(value, prefix: str, out_dict: dict):
    if value is None:
        out_dict[prefix[:-1]] = None
        return
    if hasattr(value, "get_fields_and_field_types"):
        for field_name in value.get_fields_and_field_types().keys():
            child = getattr(value, field_name)
            flatten_field_generic(child, prefix + field_name + ".", out_dict)
        return
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            out_dict[prefix[:-1]] = None
            return
        for i, elem in enumerate(value):
            flatten_field_generic(elem, prefix + str(i) + ".", out_dict)
        return
    out_dict[prefix[:-1]] = value


def flatten_msg_generic(msg):
    data = OrderedDict()
    if hasattr(msg, "header") and hasattr(msg.header, "stamp"):
        try:
            data["header.stamp.sec"] = getattr(msg.header.stamp, "sec")
            data["header.stamp.nanosec"] = getattr(msg.header.stamp, "nanosec")
        except Exception:
            pass
    flatten_field_generic(msg, "", data)
    return data


__all__ = [
    "flatten_plotjuggler",
    "flatten_msg_generic",
    "flatten_field_generic",
]
