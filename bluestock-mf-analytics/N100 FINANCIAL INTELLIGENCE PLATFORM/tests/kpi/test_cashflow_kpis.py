import pytest
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
    write_capital_allocation_csv,
)


def test_free_cash_flow():
    assert free_cash_flow(100, -30) == 70


def test_cfo_quality_score_none_when_pat_zero():
    assert cfo_quality_score([10, 20, 30], [0, 0, 0]) is None


def test_capex_intensity():
    assert pytest.approx(capex_intensity(-5, 100)) == 5.0


def test_fcf_conversion_rate_none_when_op_zero():
    assert fcf_conversion_rate(10, 0) is None


def test_capital_allocation_pattern():
    assert capital_allocation_pattern(10, -5, -2) in ("Reinvestor", "Shareholder Returns")


def test_write_capital_allocation_csv(tmp_path):
    rows = [{'company_id':'C1','year':2020,'cfo_sign':1,'cfi_sign':-1,'cff_sign':-1,'pattern_label':'Reinvestor'}]
    path = write_capital_allocation_csv(rows)
    assert path.exists()
