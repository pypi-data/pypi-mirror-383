import math

from blobjugglerpy import utils


def test_quat_to_euler_identity():
    # quaternion (1,0,0,0) -> no rotation
    r, p, y = utils.quat_to_euler(1.0, 0.0, 0.0, 0.0)
    assert math.isclose(r, 0.0, abs_tol=1e-9)
    assert math.isclose(p, 0.0, abs_tol=1e-9)
    assert math.isclose(y, 0.0, abs_tol=1e-9)


class FakeStamp:
    def __init__(self, sec, nanosec):
        self.sec = sec
        self.nanosec = nanosec


def test_time_to_float_seconds_and_header_time():
    stamp = FakeStamp(1, 500000000)
    assert utils.time_to_float_seconds(stamp) == 1.5

    class Msg:
        def __init__(self, s):
            self.header = type("H", (), {"stamp": s})()

    m = Msg(stamp)
    assert utils.header_time_sec(m) == 1.5


def test_is_numeric_sequence_and_sequence_to_list():
    assert utils.is_numeric_sequence([1, 2.0, 3])
    assert utils.sequence_to_list((1, 2, 3)) == [1, 2, 3]
    assert utils.sequence_to_list("abc") is None


def test_to_python_scalar_and_is_float_like():
    # Without numpy available, these should be identity/boolean checks
    v = 3.14
    assert utils.is_float_like(v)
    assert utils.to_python_scalar(v) == v


def test_format_csv_value_and_int_sqrt_and_publish_time():
    assert utils.format_csv_value("__time", 1.23456789) == "1.234568"
    assert utils.format_csv_value("__header_time", 1.234567890123) == "1.234567890"
    assert utils.int_sqrt(9) == 3
    assert utils.int_sqrt(10) is None
    class Msg:
        pass
    assert utils.publish_time_sec(Msg(), 1000000000) == 1.0
