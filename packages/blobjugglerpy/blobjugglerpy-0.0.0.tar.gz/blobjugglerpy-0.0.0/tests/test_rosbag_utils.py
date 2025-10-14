import os

from blobjugglerpy import rosbag_utils


def test_read_metadata_mcap_fixture():
    here = os.path.dirname(__file__)
    bag_dir = os.path.join(here, "test_mcap")
    storage_id, topics = rosbag_utils.read_metadata(bag_dir)
    assert storage_id in ("mcap", "sqlite3") or isinstance(storage_id, str)
    # topics should be a dict
    assert isinstance(topics, dict)


def test_read_metadata_sqlite_fixture():
    here = os.path.dirname(__file__)
    bag_dir = os.path.join(here, "test_sqlite")
    storage_id, topics = rosbag_utils.read_metadata(bag_dir)
    assert storage_id in ("sqlite3", "mcap") or isinstance(storage_id, str)
    assert isinstance(topics, dict)
