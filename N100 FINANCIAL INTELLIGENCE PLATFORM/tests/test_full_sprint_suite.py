import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.analytics.clustering import cluster_companies
from src.analytics.ratios import (
    asset_turnover,
    debt_to_equity,
    interest_coverage,
    net_debt,
    net_profit_margin_pct,
    operating_profit_margin_pct,
    return_on_assets_pct,
    return_on_capital_employed_pct,
    return_on_equity_pct,
)
from src.api.main import app
from src.etl.normaliser import normalize_ticker, normalize_year
from src.screener.engine import ScreenerEngine


@pytest.mark.parametrize(
    "inp, expected",
    [
        ("2020", 2020),
        ("FY20", 2020),
        ("'20", 2020),
        ("20", 2020),
        ("FY1999", 1999),
        ("99", 1999),
        ("00", 2000),
        ("49", 2049),
        ("50", 1950),
        ("FY05", 2005),
        ("2018", 2018),
        ("  2017 ", 2017),
        ("FY-21", 2021),
        ("'99", 1999),
        (None, None),
        ("n/a", None),
        ("FY\u000521", 2021),
        ("202", 202),
        ("abc2021xyz", 2021),
        ("FY 03", 2003),
        ("03", 2003),
    ],
)
def test_normalize_year_matrix(inp, expected):
    assert normalize_year(inp) == expected


@pytest.mark.parametrize(
    "inp, expected",
    [
        ("tcs.nse", "TCS"),
        ("tata_steel", "TATASTEEL"),
        (" infy ", "INFY"),
        ("reliance.NSE", "RELIANCE"),
        ("sbilife", "SBILIFE"),
        ("abc-xyz", "ABCXYZ"),
        (None, None),
        ("1234.ns", "1234"),
        ("ABCD/EX", "ABCD"),
        ("a.b-c:d_e", "ABCDE"),
        ("TCS", "TCS"),
        ("tcs.nse.in", "TCS"),
        ("t-cs", "TCS"),
        ("tcs#1", "TCS1"),
        ("tcs@nse", "TCS"),
        ("a b.c-d/e_f", "ABCDEF"),
    ],
)
def test_normalize_ticker_matrix(inp, expected):
    assert normalize_ticker(inp) == expected


@pytest.mark.parametrize(
    "net_profit,sales,expected",
    [(10, 100, 10.0), (20, 200, 10.0), (5, 50, 10.0), (0, 100, 0.0), (10, 0, None)],
)
def test_net_profit_margin_cases(net_profit, sales, expected):
    assert net_profit_margin_pct(net_profit, sales) == expected if expected is not None else net_profit_margin_pct(net_profit, sales) is None


@pytest.mark.parametrize(
    "operating_profit,sales,field,expected_opm,expected_diff",
    [(20, 100, 18, 20.0, 2.0), (15, 100, 15, 15.0, 0.0), (30, 0, 10, None, None), (10, 200, None, 5.0, None)],
)
def test_operating_profit_margin_cases(operating_profit, sales, field, expected_opm, expected_diff):
    result = operating_profit_margin_pct(operating_profit, sales, field)
    assert result[0] == expected_opm if expected_opm is not None else result[0] is None
    if expected_diff is not None:
        assert result[1] == pytest.approx(expected_diff)


@pytest.mark.parametrize(
    "net_profit,equity,reserves,expected",
    [(10.0, 100.0, 0.0, 10.0), (20.0, 200.0, 50.0, 8.0), (5.0, 0.0, 0.0, None), (5.0, -10.0, 100.0, 5.0)],
)
def test_return_on_equity_cases(net_profit, equity, reserves, expected):
    actual = return_on_equity_pct(net_profit, equity, reserves)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ebit,equity,reserves,borrowings,sector,bench,expected",
    [(10, 100, 0, 0, "Technology", None, 10.0), (20, 100, 0, 50, "Financials", 15.0, (20.0, True)), (10, 0, 0, 0, "Tech", None, (None, None))],
)
def test_return_on_capital_employed_cases(ebit, equity, reserves, borrowings, sector, bench, expected):
    result = return_on_capital_employed_pct(ebit, equity, reserves, borrowings, sector, bench)
    if isinstance(expected, tuple):
        if expected[0] is None:
            assert result[0] is None
        else:
            assert result[0] == pytest.approx(expected[0])
            assert result[1] == expected[1]
    else:
        assert result[0] == pytest.approx(expected)


@pytest.mark.parametrize(
    "net_profit,total_assets,expected",
    [(10, 200, 5.0), (20, 0, None), (25, 500, 5.0)],
)
def test_return_on_assets_cases(net_profit, total_assets, expected):
    actual = return_on_assets_pct(net_profit, total_assets)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "borrowings,equity,reserves,expected",
    [(0, 100, 0, 0.0), (10, 100, 0, 0.1), (5, 0, 0, None), (20, 50, 50, 0.2)],
)
def test_debt_to_equity_cases(borrowings, equity, reserves, expected):
    actual = debt_to_equity(borrowings, equity, reserves)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "operating_profit,other_income,interest,expected",
    [(10, 2, 0, None), (10, 2, 4, 3.0), (30, 0, 15, 2.0)],
)
def test_interest_coverage_cases(operating_profit, other_income, interest, expected):
    actual = interest_coverage(operating_profit, other_income, interest)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "borrowings,investments,expected",
    [(100, 40, 60), (0, 0, 0), (None, 10, -10), (5, None, 5)],
)
def test_net_debt_cases(borrowings, investments, expected):
    assert net_debt(borrowings, investments) == expected


@pytest.mark.parametrize(
    "sales,total_assets,expected",
    [(100, 200, 0.5), (50, 0, None), (120, 30, 4.0)],
)
def test_asset_turnover_cases(sales, total_assets, expected):
    actual = asset_turnover(sales, total_assets)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "preset,filters,expected",
    [
        ("quality_compounder", {"roe_min": 15.0, "de_max": 1.0, "fcf_min": 0.0, "revenue_cagr_5yr_min": 10.0}, 1),
        ("quality_compounder", {"de_max": 1.0}, 2),
        ("quality_compounder", {"roe_min": 20.0}, 1),
    ],
)
def test_screener_filter_matrix(preset, filters, expected):
    engine = ScreenerEngine()
    df = pd.DataFrame(
        [
            {"company_id": "C1", "roe": 16.0, "debt_to_equity": 0.8, "free_cash_flow": 10.0, "revenue_cagr_5yr": 12.0, "interest_coverage": 3.0, "composite_quality_score": 80.0, "broad_sector": "Technology"},
            {"company_id": "C2", "roe": 14.0, "debt_to_equity": 0.5, "free_cash_flow": 20.0, "revenue_cagr_5yr": 11.0, "interest_coverage": 4.0, "composite_quality_score": 75.0, "broad_sector": "Financials"},
            {"company_id": "C3", "roe": 21.0, "debt_to_equity": 1.5, "free_cash_flow": 12.0, "revenue_cagr_5yr": 8.0, "interest_coverage": 2.0, "composite_quality_score": 88.0, "broad_sector": "Technology"},
        ]
    )
    engine.config = {"presets": {preset: filters}}
    result = engine.run_preset(df, preset)
    assert len(result) == expected


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/api/v1/health", 200),
        ("/api/v1/companies", 200),
        ("/api/v1/sectors", 200),
        ("/api/v1/portfolio/stats", 200),
        ("/api/v1/companies/C001", 200),
        ("/api/v1/companies/INVALID", 404),
    ],
)
def test_api_route_matrix(client, path, expected):
    response = client.get(path)
    assert response.status_code == expected


@pytest.mark.parametrize(
    "search, sector, expected_count",
    [("C00", None, 1), (None, "Information Technology", 9), ("RELI", None, 1), ("TCS", None, 1)],
)
def test_company_filter_matrix(client, search, sector, expected_count):
    params = {}
    if search:
        params["search"] = search
    if sector:
        params["sector"] = sector
    response = client.get("/api/v1/companies", params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= expected_count


@pytest.mark.parametrize(
    "df, expected_clusters",
    [
        (
            pd.DataFrame({
                "company_id": [f"C{i:02d}" for i in range(1, 11)],
                "return_on_equity_pct": [10, 12, 13, 15, 16, 18, 20, 22, 25, 28],
                "debt_to_equity": [0.8, 0.7, 0.9, 0.6, 0.5, 0.4, 0.3, 0.2, 0.2, 0.1],
                "revenue_cagr_5yr": [4, 5, 6, 8, 9, 10, 12, 13, 14, 18],
                "fcf_cagr_5yr": [2, 3, 5, 7, 8, 10, 12, 13, 14, 16],
                "operating_profit_margin_pct": [12, 13, 14, 15, 16, 18, 20, 22, 24, 26],
            }),
            5,
        ),
        (
            pd.DataFrame({
                "company_id": [f"C{i:02d}" for i in range(1, 11)],
                "return_on_equity_pct": [8, 9, 11, 10, 12, 9, 8, 7, 9, 10],
                "debt_to_equity": [2.0, 2.1, 1.8, 2.2, 1.9, 2.3, 2.1, 2.5, 2.4, 2.0],
                "revenue_cagr_5yr": [2, 3, 2, 3, 2, 2, 1, 2, 3, 2],
                "fcf_cagr_5yr": [1, 2, 1, 2, 1, 1, 0, 1, 2, 1],
                "operating_profit_margin_pct": [8, 9, 10, 9, 11, 8, 9, 7, 8, 9],
            }),
            5,
        ),
    ],
)
def test_cluster_companies_regression(df, expected_clusters, tmp_path):
    result = cluster_companies(df, output_dir=tmp_path, reports_dir=tmp_path)
    assert set(result["cluster_id"].unique()) <= {0, 1, 2, 3, 4}
    assert len(result) == len(df)
    assert (tmp_path / "cluster_labels.csv").exists()
    assert result["cluster_name"].notna().all()
    assert "distance_from_centroid" in result.columns


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/api/v1/companies/C001/pl", 200),
        ("/api/v1/companies/C001/bs", 200),
        ("/api/v1/companies/C001/cashflow", 200),
        ("/api/v1/companies/C001/ratios", 200),
        ("/api/v1/companies/C001/documents", 200),
        ("/api/v1/screener?min_roe=10", 200),
        ("/api/v1/sectors/Information%20Technology/companies", 200),
    ],
)
def test_additional_api_routes(client, path, expected):
    response = client.get(path)
    assert response.status_code == expected


@pytest.mark.parametrize(
    "func_name,args,expected",
    [
        ("normalize_year", ("FY20",), 2020),
        ("normalize_ticker", ("tcs.nse",), "TCS"),
        ("net_profit_margin_pct", (10, 100), 10.0),
        ("return_on_assets_pct", (10, 200), 5.0),
        ("debt_to_equity", (0, 100, 0), 0.0),
        ("interest_coverage", (10, 2, 0), None),
        ("net_debt", (100, 40), 60),
        ("asset_turnover", (100, 200), 0.5),
    ],
)
def test_core_helpers_func_matrix(func_name, args, expected):
    import src.analytics.ratios as r
    fn = getattr(r, func_name)
    out = fn(*args)
    if expected is None:
        assert out is None
    else:
        assert out == pytest.approx(expected)
