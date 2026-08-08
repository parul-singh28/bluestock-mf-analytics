import pandas as pd
from src.analytics.peer import compute_peer_percentiles


def test_peer_percentiles_inversion():
    ratios = pd.DataFrame(
        [
            {"company_id": "C1", "peer_group_name": "IT Services", "debt_to_equity": 0.5, "return_on_equity_pct": 20.0, "year": 2024},
            {"company_id": "C2", "peer_group_name": "IT Services", "debt_to_equity": 1.0, "return_on_equity_pct": 15.0, "year": 2024},
        ]
    )
    company_meta = pd.DataFrame(
        [{"company_id": "C1", "peer_group_name": "IT Services"}, {"company_id": "C2", "peer_group_name": "IT Services"}]
    )
    result = compute_peer_percentiles(ratios, company_meta)
    assert any((result["metric"] == "debt_to_equity") & (result["company_id"] == "C1"))
    dte_ranks = result[result["metric"] == "debt_to_equity"]["percentile_rank"].tolist()
    assert dte_ranks[0] > dte_ranks[1]
