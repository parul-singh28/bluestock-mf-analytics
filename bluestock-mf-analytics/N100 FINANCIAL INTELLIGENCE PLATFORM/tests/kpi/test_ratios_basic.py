import pytest
from src.analytics.ratios import (
    net_profit_margin_pct,
    operating_profit_margin_pct,
    return_on_equity_pct,
    return_on_capital_employed_pct,
    return_on_assets_pct,
    debt_to_equity,
    interest_coverage,
    net_debt,
    asset_turnover,
)


def test_net_profit_margin_normal():
    assert pytest.approx(net_profit_margin_pct(10, 100)) == 10.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin_pct(10, 0) is None


def test_operating_profit_margin_and_diff():
    opm, diff = operating_profit_margin_pct(20, 100, 18)
    assert pytest.approx(opm, rel=1e-3) == 20.0
    assert pytest.approx(diff, rel=1e-3) == 2.0


def test_return_on_equity_none_negative_equity():
    assert return_on_equity_pct(10, -5, 0) is None


def test_return_on_assets():
    assert pytest.approx(return_on_assets_pct(10, 200)) == 5.0


def test_debt_to_equity_zero_borrowings():
    assert debt_to_equity(0, 100, 0) == 0.0


def test_interest_coverage_none_when_interest_zero():
    assert interest_coverage(10, 2, 0) is None


def test_net_debt_calc():
    assert net_debt(100, 40) == 60


def test_asset_turnover_none_when_assets_zero():
    assert asset_turnover(100, 0) is None
