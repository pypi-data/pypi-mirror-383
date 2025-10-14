# blobjugglerpy

Export ROS2 rosbag2 to CSV in PlotJuggler style or per-topic.

## Usage

Python API:

```python
from blobjugglerpy import collect_columns_plotjuggler, write_plotjuggler_csv

columns, storage_id, type_cache = collect_columns_plotjuggler(bag_dir, topics_filter=None)
write_plotjuggler_csv(bag_dir, out_csv_path, columns, storage_id, topics_filter=None, type_cache=type_cache)
```

CLI:

```bash
python -m blobjugglerpy --bag /path/to/bag --out /path/to/out.csv --all
```

Topic selection supports glob-style patterns via `--topics`, for example:

```bash
python -m blobjugglerpy --bag /path/to/bag --out out.csv --topics "/log*" "/sensors/*"
```

Note: You must specify either `--all` or `--topics` (supports globs).

## Command Line Help

```bash
$ python -m blobjugglerpy -h
usage: __main__.py [-h] --bag BAG --out OUT [--topics [TOPICS ...]] [--all] [--per-topic] [--no-sort]

Export ROS2 bag to CSV (PlotJuggler-style by default).

options:
  -h, --help            show this help message and exit
  --bag BAG             Path to rosbag2 directory (contains metadata.yaml)
  --out OUT             Output CSV path (default) or directory when --per-topic
  --topics [TOPICS ...]
                        Explicit list of topics to export
  --all                 Export all topics in the bag
  --per-topic           Write one CSV per topic instead of merged
  --no-sort             Do not sort by __time
```

## Installation

```bash
pip install git+https://github.com/incebellipipo/blobjugglerpy.git
```
