import polars as pl
import numpy as np
import pytest
from polars.testing import assert_series_equal
from functime.feature_extraction.tsfresh_mathieu  import benford_correlation, _get_length_sequences_where, longest_strike_below_mean, longest_strike_above_mean, mean_n_absolute_max, percent_reocurring_points, percent_recoccuring_values, sum_reocurring_points, sum_reocurring_values

def test_benford_correlation():
    # Nan, division by 0
    X_uniform = pl.Series([1, 2, 3, 4, 5, 6, 7, 8, 9])
    # Random serie
    X_random = pl.Series([26.24, 3.03, -2.92, 3.5, -0.07, 0.35, 0.10, 0.51, -0.43])
    # Fibo, distribution same as benford law
    X_fibo = [0, 1]
    for i in range(2, 50):
        X_fibo.append(X_fibo[i - 1] + X_fibo[i - 2])
    
    assert np.isnan(benford_correlation(X_uniform))
    assert benford_correlation(X_random) == 0.39753280229716703
    assert benford_correlation(pl.Series(X_fibo)) == 0.9959632739083689


@pytest.mark.parametrize("S, res", [
    (
        [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1],
        [1, 3, 1, 2]
    ),
    (
        [0, True, 0, 0, True, True, True, 0, 0, True, 0, True, True],
        [1, 3, 1, 2]
    ),
    (
        [0, True, 0, 0, 1, True, 1, 0, 0, True, 0, 1, True],
        [1, 3, 1, 2]
    )
])
def test__get_length_sequences_where(S, res):
    assert_series_equal(
        _get_length_sequences_where(pl.Series(S)),
        pl.Series("count", res, dtype=pl.UInt32)
    )


@pytest.mark.parametrize("S, res", [
    ([1, 2, 1, 1, 1, 2, 2, 2], 3),
    ([1, 2, 3, 4, 5, 6], 3),
    ([1, 2, 3, 4, 5], 2),
    ([1, 2, 1], 1),
    ([1, 1, 1], 0),
    ([], 0)
])
def test_longest_strike_below_mean(S, res):
    assert longest_strike_below_mean(pl.Series(S)) == res


@pytest.mark.parametrize("S, res", [
    ([1, 2, 1, 2, 1, 2, 2, 1], 2),
    ([1, 2, 3, 4, 5, 6], 3),
    ([1, 2, 3, 4, 5], 2),
    ([1, 2, 1], 1),
    ([1, 1, 1], 0),
    ([], 0)
])
def test_longest_strike_above_mean(S, res):
    assert longest_strike_above_mean(pl.Series(S)) == res

@pytest.mark.parametrize("S, n_max, res", [
    ([], 1, None),
    ([12, 3], 10, None),
    ([-1, -5, 4, 10], 3, 6.333333333333333),
    ([0, -5, -9], 2, 7.000000),
    ([0, 0, 0], 1, 0)
])
def test_mean_n_absolute_max(S, n_max, res):
    assert mean_n_absolute_max(x = pl.Series(S), n_maxima = n_max) == res

def test_mean_n_absolute_max_value_error():
    with pytest.raises(ValueError):
        mean_n_absolute_max(
            x = pl.Series([12, 3]),
            n_maxima = 0
        )
    with pytest.raises(ValueError):
        mean_n_absolute_max(
            x = pl.Series([12, 3]),
            n_maxima = -1
        )
@pytest.mark.parametrize("S, res", [
    ([1, 1, 2, 3, 4], 0.4),
    ([1, 1.5, 2, 3], 0),
    ([1], 0),
    ([1.111, -2.45, 1.111, 2.45], 0.5)
])
def test_percent_reocurring_points(S, res):
    assert percent_reocurring_points(pl.Series(S)) == res

def test_percent_reocurring_points_value_error():
    with pytest.raises(ValueError):
        percent_reocurring_points(pl.Series([]))

@pytest.mark.parametrize("S, res", [
    ([1, 1, 2, 3, 4], 0.25),
    ([1, 1.5, 2, 3], 0),
    ([1], 0),
    ([1.111, -2.45, 1.111, 2.45], 1.0 / 3.0)
])
def test_percent_recoccuring_values(S, res):
    assert percent_recoccuring_values(pl.Series(S)) == res

def test_percent_recoccuring_values_value_error():
    with pytest.raises(ValueError):
        percent_recoccuring_values(pl.Series([]))

@pytest.mark.parametrize("S, res", [
    ([1, 1, 2, 3, 4, 4], 10),
    ([1, 1.5, 2, 3], 0),
    ([1], 0),
    ([1.111, -2.45, 1.111, 2.45], 2.222),
    ([], 0)
])
def test_sum_reocurring_points(S, res):
    assert sum_reocurring_points(pl.Series(S)) == res


@pytest.mark.parametrize("S, res", [
    ([1, 1, 2, 3, 4, 4], 5),
    ([1, 1.5, 2, 3], 0),
    ([1], 0),
    ([1.111, -2.45, 1.111, 2.45], 1.111),
    ([], 0)
])
def test_sum_reocurring_values(S, res):
    assert sum_reocurring_values(pl.Series(S)) == res