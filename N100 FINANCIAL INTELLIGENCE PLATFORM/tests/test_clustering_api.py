import pandas as pd
from fastapi.testclient import TestClient

from src.analytics.clustering import cluster_companies
from src.api.main import app


def test_cluster_companies_assigns_five_clusters_and_writes_outputs(tmp_path):
    df = pd.DataFrame(
        {
            "company_id": [f"C{i:02d}" for i in range(1, 21)],
            "return_on_equity_pct": [10, 12, 13, 14, 15, 20, 22, 24, 26, 28, 8, 9, 11, 16, 18, 25, 27, 29, 30, 31],
            "debt_to_equity": [0.6, 0.7, 0.8, 0.9, 1.0, 0.3, 0.2, 0.1, 0.1, 0.2, 2.5, 2.8, 3.1, 1.5, 1.4, 0.5, 0.7, 0.6, 0.4, 0.3],
            "revenue_cagr_5yr": [4, 5, 6, 7, 8, 12, 13, 15, 17, 18, 2, 3, 5, 9, 10, 14, 16, 19, 21, 22],
            "fcf_cagr_5yr": [3, 4, 5, 6, 7, 11, 12, 14, 15, 17, 2, 4, 5, 8, 9, 13, 15, 18, 20, 21],
            "operating_profit_margin_pct": [10, 12, 14, 15, 16, 18, 20, 22, 24, 26, 7, 8, 9, 11, 13, 19, 21, 23, 25, 27],
        }
    )
    result = cluster_companies(df, output_dir=tmp_path, reports_dir=tmp_path)
    assert set(result["cluster_id"].unique()) == {0, 1, 2, 3, 4}
    assert "cluster_name" in result.columns
    assert "distance_from_centroid" in result.columns
    assert (tmp_path / "cluster_labels.csv").exists()


def test_api_health_and_company_listing():
    client = TestClient(app)
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    payload = health.json()
    assert payload["status"] == "ok"
    assert "db_row_counts" in payload

    companies = client.get("/api/v1/companies")
    assert companies.status_code == 200
    data = companies.json()
    assert isinstance(data, list)
    assert len(data) >= 1
