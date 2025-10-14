import os
import csv

from types import SimpleNamespace

from blobjugglerpy import csv_export


class FakeReader:
    def __init__(self, topics):
        # topics: list of tuples (topic, data, time_ns, msg)
        self._topics = topics
        self._i = 0

    def get_all_topics_and_types(self):
        # return info objects with name and type
        return [SimpleNamespace(name=t[0], type=t[1].__name__ if hasattr(t[1],'__name__') else t[1]) for t in self._topics]

    def has_next(self):
        return self._i < len(self._topics)

    def read_next(self):
        topic, data, t, msg = self._topics[self._i]
        self._i += 1
        return topic, data, t


class FakeMsg:
    def __init__(self, header_stamp=None, **fields):
        if header_stamp is not None:
            self.header = SimpleNamespace(stamp=SimpleNamespace(sec=header_stamp[0], nanosec=header_stamp[1]))
        for k, v in fields.items():
            setattr(self, k, v)

    def get_fields_and_field_types(self):
        return {k: type(v).__name__ for k, v in self.__dict__.items() if k != 'header'}


def test_write_plotjuggler_csv_monkeypatched(tmp_path, monkeypatch):
    # Prepare a fake message with a simple field
    msg = FakeMsg(header_stamp=(1, 0), value=3.1415)

    # Fake deserialize_message just returns our msg
    monkeypatch.setattr(csv_export, 'deserialize_message', lambda data, typ: msg)

    # Fake get_message (not used heavily here)
    monkeypatch.setattr(csv_export, 'get_message', lambda typ: None)

    # Fake reader that yields one topic
    topic = '/my/topic'
    # Make make_reader return a fresh FakeReader each call so it's not exhausted
    def make_fake_reader(bag_dir, storage_id):
        return FakeReader([(topic, None, 1000000000, msg)])

    monkeypatch.setattr(csv_export, 'make_reader', make_fake_reader)

    # Also monkeypatch read_metadata used by collect_columns_plotjuggler
    monkeypatch.setattr(csv_export, 'read_metadata', lambda bag_dir: ('sqlite3', {topic: 'FakeType'}))

    # Now call collect_columns_plotjuggler
    columns, storage_id, type_cache = csv_export.collect_columns_plotjuggler('dummy', topics_filter=None)
    assert '__time' in columns

    out_csv = tmp_path / 'out.csv'
    # Call write_plotjuggler_csv with columns
    csv_export.write_plotjuggler_csv('dummy', str(out_csv), columns, storage_id, topics_filter=None, type_cache=type_cache)

    # Check file exists and has expected header and at least one data row
    assert out_csv.exists()
    with open(out_csv, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 1
    # Expect the __time column to be present and formatted
    assert '__time' in reader.fieldnames
