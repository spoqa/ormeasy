from pytest import raises
from ormeasy.common import get_all_modules


def test_get_all_modules():
    assert get_all_modules('os') == {'os'}
    assert get_all_modules('urllib') == {
        'urllib.error',
        'urllib.parse',
        'urllib.robotparser',
        'urllib.response',
        'urllib.request',
    }
    with raises(ValueError):
        assert get_all_modules('asdf')


def test_get_all_sub_modules():
    assert get_all_modules('urllib.error') == {
        'urllib.error',
    }
