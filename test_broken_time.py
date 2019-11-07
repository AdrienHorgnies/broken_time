import broken_time
import mock
import pytest

bt = broken_time.BrokenTime


def test_init_nominal():
    t = bt(1, 1, 1)

    assert t.hours == 1
    assert t.minutes == 1
    assert t.seconds == 1
    # noinspection PyProtectedMember
    assert t._seconds == 3661


def test_init_overflow():
    t = bt(25, 90, 90)

    assert t.hours == 26
    assert t.minutes == 31
    assert t.seconds == 30
    # noinspection PyProtectedMember
    assert t._seconds == 95490


def test_str_one_digit():
    t = bt(1, 1, 1)

    assert str(t) == '01:01:01'


def test_str_two_digits():
    t = bt(11, 1, 1)

    assert str(t) == '11:01:01'


def test_str_three():
    t = bt(100, 1, 1)

    assert str(t) == '100:01:01'


def test_cast_args_convert_str():
    mock_function = mock.MagicMock()
    decorated = bt.Decorators.cast_args(mock_function)

    decorated('01:01:01')
    mock_function.assert_called_with(bt(1, 1, 1))


def test_cast_args_skips_bt():
    mock_function = mock.MagicMock()
    decorated = bt.Decorators.cast_args(mock_function)

    t = bt(1, 1, 1)
    decorated(t)

    mock_function.assert_called_with(t)


def test_cast_args_skips_after():
    mock_function = mock.MagicMock()
    decorated = bt.Decorators.cast_args(after=0)(mock_function)

    decorated(1, '01:01:01')

    mock_function.assert_called_with(1, bt(1, 1, 1))


def test_cast_args_raises_value_error():
    mock_function = mock.MagicMock()
    decorated = bt.Decorators.cast_args(mock_function)

    with pytest.raises(ValueError):
        decorated(1)


def test_cast_args_add():
    assert bt(1, 1, 1) + '00:00:01' == bt(1, 1, 2)


def test_add_positive():
    assert bt(1, 1, 1) + bt(0, 1, 1) == bt(1, 2, 2)
    assert bt(1, 1, 1) + bt(1, 0, 0) == bt(2, 1, 1)
    assert bt(1, 59, 59) + bt(0, 0, 1) == bt(2, 0, 0)


def test_add_neutral():
    assert bt(1, 1, 1) + bt(0, 0, 0) == bt(1, 1, 1)


def test_add_negative():
    assert bt(1, 1, 1) + bt(0, -1, -1) == bt(1, 0, 0)
    assert bt(1, 1, 1) + bt(-1, -1, -1) == bt(0, 0, 0)
    assert bt(1, 1, 1) + bt(-2, -2, -2) == bt(-1, -1, -1)


def test_sub_positive():
    assert bt(1, 1, 1) - bt(0, 1, 1) == bt(1, 0, 0)
    assert bt(1, 1, 1) - bt(1, 1, 1) == bt(0, 0, 0)
    assert bt(1, 1, 1) - bt(2, 2, 2) == bt(-1, -1, -1)


def test_sub_neutral():
    assert bt(1, 1, 1) - bt(0, 0, 0) == bt(1, 1, 1)


def test_sub_negative():
    assert bt(1, 1, 1) - bt(0, -1, -1) == bt(1, 2, 2)
    assert bt(1, 1, 1) - bt(-1, -1, -1) == bt(2, 2, 2)
    assert bt(-1, -1, -1) - bt(-1, -1, -1) == bt(0, 0, 0)


def test_mul_negative():
    assert bt(1, 1, 1).mul(-1) == bt(-1, -1, -1)


def test_mul_neutral():
    assert bt(1, 1, 1).mul(1) == bt(1, 1, 1)


def test_mul_positive():
    assert bt(1, 1, 1).mul(2) == bt(2, 2, 2)


def test_mul_float():
    assert bt(1, 1, 1).mul(1.5) == bt(1, 31, 32)

