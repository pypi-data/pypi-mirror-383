"""
ROS 2 rosbag reader helpers and environment checks.
"""

from __future__ import annotations

import os
import yaml

try:
    import rosbag2_py
    from rclpy.serialization import deserialize_message  # re-export convenience
    from rosidl_runtime_py.utilities import get_message  # re-export convenience
except Exception:  # pragma: no cover - ROS2 may be unavailable in some envs
    rosbag2_py = None
    deserialize_message = None
    get_message = None


def require_ros2() -> None:
    if rosbag2_py is None or deserialize_message is None or get_message is None:
        raise RuntimeError("ROS2 environment not detected. Please source your ROS2 workspace.")


def read_metadata(bag_dir: str):
    meta_path = os.path.join(bag_dir, "metadata.yaml")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"metadata.yaml not found in {bag_dir}")
    with open(meta_path, "r") as f:
        meta = yaml.safe_load(f) or {}

    storage_id = meta.get("storage_identifier")
    topics_list = meta.get("topics_with_message_count")

    info = meta.get("rosbag2_bagfile_information") or {}
    if storage_id is None:
        storage_id = info.get("storage_identifier")
    if topics_list is None:
        topics_list = info.get("topics_with_message_count")

    storage_obj = meta.get("storage") or info.get("storage") or {}
    if storage_id is None and isinstance(storage_obj, dict):
        storage_id = storage_obj.get("storage_identifier")

    if storage_id is None:
        storage_id = "sqlite3"

    topics_type_map = {}
    if isinstance(topics_list, list):
        for t in topics_list:
            tm = t.get("topic_metadata") if isinstance(t, dict) else None
            if isinstance(tm, dict):
                name = tm.get("name")
                typ = tm.get("type")
                if name and typ:
                    topics_type_map[name] = typ
            else:
                name = t.get("name") if isinstance(t, dict) else None
                typ = t.get("type") if isinstance(t, dict) else None
                if name and typ:
                    topics_type_map[name] = typ
    return storage_id, topics_type_map


def try_open_reader(storage_id: str, bag_dir: str, serialization_format: str = "cdr"):
    storage_options = rosbag2_py.StorageOptions(uri=bag_dir, storage_id=storage_id)
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format=serialization_format,
        output_serialization_format=serialization_format,
    )
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def make_reader(bag_dir: str, storage_id: str, serialization_format: str = "cdr"):
    try_order = [storage_id]
    for cand in ("sqlite3", "mcap"):
        if cand not in try_order:
            try_order.append(cand)
    last_err = None
    for sid in try_order:
        try:
            return try_open_reader(sid, bag_dir, serialization_format)
        except Exception as e:  # pragma: no cover - depends on env
            last_err = e
            continue
    raise RuntimeError(
        f"Failed to open bag with storage ids {try_order}. Last error: {last_err}"
    )


__all__ = [
    "require_ros2",
    "read_metadata",
    "make_reader",
    "deserialize_message",
    "get_message",
]
