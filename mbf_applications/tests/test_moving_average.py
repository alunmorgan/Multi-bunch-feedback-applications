# import pytest
from mbf_applications.Common.moving_average import movingAverage


def test_returns_original_with_n_is_1():
    assert all(movingAverage([1, 2, 3, 4], n=1) == [1, 2, 3, 4])