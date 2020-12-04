from mbf_applications.Common.moving_average import movingAverage


def test_returns_original_with_n_is_1():
    assert all(movingAverage([1, 2, 3, 4], n=1) == [1, 2, 3, 4])

def test_returns_expected_with_n_is_2():
    print(movingAverage([1, 2, 3, 4], n=2))
    assert all(movingAverage([1, 2, 3, 4], n=2) == [1.5, 2.5, 3.5])