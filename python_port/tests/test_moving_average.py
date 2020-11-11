import pytest
from Common import movingAverage


def test_returns_original_with_n_is_1():
    assert movingAverage([1, 2, 3, 4], n=1) == [1, 2, 3, 4]