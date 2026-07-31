import pandas as pd
from src.screener.engine import ScreenerEngine


def make_df():
    return pd.DataFrame(
        [
            {"company_id": "C1", "roe": 16.0, "debt_to_equity": 0.8, "free_cash_flow": 10.0, "revenue_cagr_5yr": 12.0, "interest_coverage": 3.0, "composite_quality_score": 80.0, "broad_sector": "Technology"},
            {"company_id": "C2", "roe": 14.0, "debt_to_equity": 0.5, "free_cash_flow": 20.0, "revenue_cagr_5yr": 11.0, "interest_coverage": 4.0, "composite_quality_score": 75.0, "broad_sector": "Financials"},
        ]
    )


def test_quality_compounder_preset():
    engine = ScreenerEngine()
    df = make_df()
    engine.config = {"presets": {"quality_compounder": {"roe_min": 15.0, "de_max": 1.0, "fcf_min": 0.0, "revenue_cagr_5yr_min": 10.0}}}
    result = engine.run_preset(df, "quality_compounder")
    assert len(result) == 1
    assert result.iloc[0]["company_id"] == "C1"


def test_de_max_skips_financials():
    engine = ScreenerEngine()
    df = make_df()
    engine.config = {"presets": {"quality_compounder": {"de_max": 1.0}}}
    result = engine.run_preset(df, "quality_compounder")
    assert "C2" in result["company_id"].tolist()
