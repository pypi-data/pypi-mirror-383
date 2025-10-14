"""
High-level CSV export functions for PlotJuggler-style and per-topic outputs.
"""

from __future__ import annotations

import os
import csv
from collections import defaultdict

from .rosbag_utils import read_metadata, make_reader, get_message, deserialize_message
import fnmatch
from .flatteners import flatten_plotjuggler, flatten_msg_generic
from .utils import header_time_sec, publish_time_sec, format_csv_value


def collect_columns_plotjuggler(bag_dir, topics_filter):
    storage_id, topic_type_map = read_metadata(bag_dir)
    type_cache = {}
    for typ in set(topic_type_map.values()):
        try:
            type_cache[typ] = get_message(typ)
        except Exception:
            pass

    wanted = list(topics_filter) if topics_filter is not None else None
    columns = set()

    reader = make_reader(bag_dir, storage_id)
    try:
        topic_type_by_name = {info.name: info.type for info in reader.get_all_topics_and_types()}
        while reader.has_next():
            topic, data, t = reader.read_next()
            if wanted is not None and not any(fnmatch.fnmatch(topic, pat) for pat in wanted):
                continue
            typ = topic_type_by_name.get(topic)
            if typ not in type_cache:
                try:
                    type_cache[typ] = get_message(typ)
                except Exception:
                    continue
            msg = deserialize_message(data, type_cache[typ])
            flat = flatten_plotjuggler(msg, topic)
            header_ts = header_time_sec(msg)
            columns.update(flat.keys())
            if header_ts is not None:
                columns.add("__header_time")
    finally:
        del reader

    # Order: __time, __header_time (if present), then the rest sorted
    has_header_time = "__header_time" in columns
    other_cols = sorted([c for c in columns if c != "__header_time"])
    header = ["__time"] + (["__header_time"] if has_header_time else []) + other_cols
    return header, storage_id, type_cache


def write_plotjuggler_csv(
    bag_dir,
    out_csv_path,
    columns,
    storage_id,
    topics_filter,
    type_cache,
    sort_rows: bool = True,
):
    wanted = list(topics_filter) if topics_filter is not None else None
    rows = []

    reader = make_reader(bag_dir, storage_id)
    topic_type_by_name = {info.name: info.type for info in reader.get_all_topics_and_types()}

    while reader.has_next():
        topic, data, t = reader.read_next()
        if wanted is not None and not any(fnmatch.fnmatch(topic, pat) for pat in wanted):
            continue
        typ = topic_type_by_name.get(topic)
        if typ not in type_cache:
            try:
                type_cache[typ] = get_message(typ)
            except Exception:
                continue
        msg = deserialize_message(data, type_cache[typ])
        flat = flatten_plotjuggler(msg, topic)
        ts = publish_time_sec(msg, int(t))
        header_ts = header_time_sec(msg)
        row = {"__time": ts}
        if header_ts is not None:
            row["__header_time"] = header_ts
        row.update(flat)
        rows.append(row)

    if sort_rows:
        rows.sort(key=lambda r: r.get("__time", 0.0))

    parent = os.path.dirname(os.path.abspath(out_csv_path)) or "."
    os.makedirs(parent, exist_ok=True)
    with open(out_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            row_out = {}
            for c in columns:
                row_out[c] = format_csv_value(c, r.get(c))
            writer.writerow(row_out)


def collect_columns_generic(bag_dir, topics_filter):
    storage_id, topic_type_map = read_metadata(bag_dir)
    type_cache = {}
    for typ in set(topic_type_map.values()):
        try:
            type_cache[typ] = get_message(typ)
        except Exception:
            pass
    wanted = list(topics_filter) if topics_filter is not None else None

    columns = defaultdict(set)
    reader = make_reader(bag_dir, storage_id)
    try:
        topic_type_by_name = {info.name: info.type for info in reader.get_all_topics_and_types()}
        while reader.has_next():
            topic, data, t = reader.read_next()
            if wanted is not None and not any(fnmatch.fnmatch(topic, pat) for pat in wanted):
                continue
            typ = topic_type_by_name.get(topic)
            if typ not in type_cache:
                try:
                    type_cache[typ] = get_message(typ)
                except Exception:
                    continue
            msg = deserialize_message(data, type_cache[typ])
            row = flatten_msg_generic(msg)
            row["bag_time.nanoseconds"] = int(t)
            for k in row.keys():
                columns[topic].add(k)
    finally:
        del reader
    sorted_columns = {}
    for tp, cols in columns.items():
        cols_sorted = sorted([c for c in cols if c != "bag_time.nanoseconds"])
        sorted_columns[tp] = ["bag_time.nanoseconds"] + cols_sorted
    return sorted_columns, storage_id, type_cache


def write_csvs(bag_dir, out_dir, topic_columns, storage_id, type_cache):
    os.makedirs(out_dir, exist_ok=True)
    files = {}
    writers = {}
    try:
        for topic, cols in topic_columns.items():
            name = topic.strip("/").replace("/", "_")
            name = (name or "root") + ".csv"
            path = os.path.join(out_dir, name)
            f = open(path, "w", newline="")
            files[topic] = f
            writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            writers[topic] = writer
            writer.writeheader()

        reader = make_reader(bag_dir, storage_id)
        topic_type_by_name = {info.name: info.type for info in reader.get_all_topics_and_types()}

        while reader.has_next():
            topic, data, t = reader.read_next()
            if topic not in topic_columns:
                continue
            typ = topic_type_by_name.get(topic)
            if typ not in type_cache:
                try:
                    type_cache[typ] = get_message(typ)
                except Exception:
                    continue
            msg = deserialize_message(data, type_cache[typ])
            row = flatten_msg_generic(msg)
            row["bag_time.nanoseconds"] = int(t)
            for k in topic_columns[topic]:
                if k not in row:
                    row[k] = None
            writers[topic].writerow(row)
    finally:
        for f in files.values():
            try:
                f.close()
            except Exception:
                pass


__all__ = [
    "collect_columns_plotjuggler",
    "write_plotjuggler_csv",
    "collect_columns_generic",
    "write_csvs",
]
