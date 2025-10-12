import pytest

_counter = {"attempts": 0}


@pytest.mark.smart_rerun(max=3, delay=0)
def test_flaky_counter_passes_on_second_attempt():
    _counter["attempts"] += 1
    if _counter["attempts"] < 2:
        pytest.fail("Intentional flaky failure")
    assert True


def test_regular_behavior_without_marker():
    assert 1 + 1 == 2
