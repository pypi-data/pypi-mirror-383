"""
Command-line interface for exporting ROS2 rosbag2 to CSV.
"""

from __future__ import annotations

import os
import argparse

from .rosbag_utils import require_ros2
from .csv_export import (
    collect_columns_plotjuggler,
    write_plotjuggler_csv,
    collect_columns_generic,
    write_csvs,
)


def main(argv: list[str] | None = None) -> None:
    require_ros2()
    parser = argparse.ArgumentParser(description="Export ROS2 bag to CSV (PlotJuggler-style by default).")
    parser.add_argument("--bag", required=True, help="Path to rosbag2 directory (contains metadata.yaml)")
    parser.add_argument("--out", required=True, help="Output CSV path (default) or directory when --per-topic")
    parser.add_argument("--topics", nargs="*", default=None, help="Explicit list of topics to export")
    parser.add_argument("--all", action="store_true", help="Export all topics in the bag")
    parser.add_argument("--per-topic", action="store_true", help="Write one CSV per topic instead of merged")
    parser.add_argument("--no-sort", action="store_true", help="Do not sort by __time")
    args = parser.parse_args(argv)

    bag_dir = args.bag
    out_target = args.out

    if not os.path.isdir(bag_dir):
        raise FileNotFoundError(f"Bag directory not found: {bag_dir}")
    if not os.path.exists(os.path.join(bag_dir, "metadata.yaml")):
        raise FileNotFoundError(f"metadata.yaml not found in: {bag_dir}")

    if args.all:
        topics_filter = None  # None means include all topics
    elif args.topics:
        topics_filter = args.topics
    else:
        # No default topics anymore: force user to choose explicitly
        parser.error("Please specify either --all or --topics <patterns> (supports globs like '/log*').")

    if args.per_topic:
        topic_columns, storage_id, type_cache = collect_columns_generic(bag_dir, topics_filter)
        if not topic_columns:
            print("No matching topics found.")
            return
        write_csvs(bag_dir, out_target, topic_columns, storage_id, type_cache)
        print("Done. Wrote per-topic CSVs to:", out_target)
        return

    columns, storage_id, type_cache = collect_columns_plotjuggler(bag_dir, topics_filter)
    write_plotjuggler_csv(
        bag_dir=bag_dir,
        out_csv_path=out_target,
        columns=columns,
        storage_id=storage_id,
        topics_filter=topics_filter,
        type_cache=type_cache,
        sort_rows=(not args.no_sort),
    )
    print("Done. Wrote PlotJuggler-style CSV:", out_target)


__all__ = ["main"]
