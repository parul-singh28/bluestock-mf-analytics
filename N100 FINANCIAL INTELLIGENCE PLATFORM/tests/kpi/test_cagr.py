import pytest
from src.analytics.cagr import compute_cagr, CAGRFlag, cagr_from_series


def test_cagr_normal():
    val, flag = compute_cagr(100, 125, 2)
    assert flag is None
    # compute_cagr returns percent, so compare to fractional*100
    expected_pct = ((125/100)**(1/2) - 1) * 100
    assert pytest.approx(val, rel=1e-3) == expected_pct


def test_cagr_zero_base():
    val, flag = compute_cagr(0, 50, 3)
    assert val is None and flag == CAGRFlag.ZERO_BASE


def test_cagr_turnaround():
    val, flag = compute_cagr(-10, 20, 2)
    assert val is None and flag == CAGRFlag.TURNAROUND


def test_cagr_decline_to_loss():
    val, flag = compute_cagr(10, -5, 3)
    assert val is None and flag == CAGRFlag.DECLINE_TO_LOSS


def test_cagr_insufficient_series():
    vals = [100, 120]
    years = [2019, 2020]
    val, flag = cagr_from_series(vals, years, 5)
    assert val is None and flag == CAGRFlag.INSUFFICIENT
