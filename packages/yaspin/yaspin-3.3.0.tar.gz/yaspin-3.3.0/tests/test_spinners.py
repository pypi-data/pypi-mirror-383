"""
tests.test_spinners
~~~~~~~~~~~~~~~~~~~

Tests for spinners collection.
"""

from collections import OrderedDict

import json

import pytest

from yaspin.spinners import Spinners, SPINNERS_DATA

spinners_dict = OrderedDict(json.loads(SPINNERS_DATA))
test_cases = [(name, v["frames"], v["interval"]) for name, v in spinners_dict.items()]


def test_len():
    assert len(Spinners) == len(spinners_dict)


# Entry example:
# ('balloon', [' ', '.', 'o', 'O', '@', '*', ' '], 140)
@pytest.mark.parametrize("name, frames, interval", test_cases)
def test_spinners(name, frames, interval):
    assert getattr(Spinners, name).frames == frames
    assert getattr(Spinners, name).interval == interval
