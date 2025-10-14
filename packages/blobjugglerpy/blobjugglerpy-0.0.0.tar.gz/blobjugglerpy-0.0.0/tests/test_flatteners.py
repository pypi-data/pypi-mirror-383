from collections import OrderedDict

from blobjugglerpy import flatteners


class SimpleMsg:
    def __init__(self, **fields):
        for k, v in fields.items():
            setattr(self, k, v)

    def get_fields_and_field_types(self):
        # emulate ROS message helper
        return {k: type(v).__name__ for k, v in self.__dict__.items()}


def test_flatten_plotjuggler_simple():
    # msg with header.stamp
    stamp = type("S", (), {"sec": 2, "nanosec": 0})()
    header = type("H", (), {"stamp": stamp})()
    msg = SimpleMsg(header=header, value=42)
    out = flatteners.flatten_plotjuggler(msg, "/topic")
    # expect keys like /topic/header/stamp/sec and /topic/value
    assert "/topic/value" in out


def test_flatten_field_generic_and_msg_generic():
    # nested structure and sequences
    inner = SimpleMsg(a=1, b=[2, 3])
    msg = SimpleMsg(header=type("H", (), {"stamp": type("S", (), {"sec": 1, "nanosec": 0})()})(), nested=inner)
    d = {}
    flatteners.flatten_field_generic(msg.nested, "nested.", d)
    # expect nested.a and nested.b.0 etc
    assert "nested.a" in d
    assert "nested.b.0" in d

    gen = flatteners.flatten_msg_generic(msg)
    assert "nested.a" in gen
    assert "header.stamp.sec" in gen
