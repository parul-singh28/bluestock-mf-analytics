"""Peer percentile ranking engine."""
import sqlite3
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "nifty100.db"
OUTPUT = ROOT / "output"

METRICS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]


def percent_rank(series: pd.Series) -> pd.Series:
    return series.rank(pct=True, method="min")


def compute_peer_percentiles(ratios: pd.DataFrame, company_meta: pd.DataFrame) -> pd.DataFrame:
    merged = ratios.merge(
        company_meta[["company_id", "peer_group_name"]],
        on="company_id",
        how="left",
        suffixes=("", "_meta"),
    )
    if "peer_group_name_meta" in merged.columns:
        if "peer_group_name" in merged.columns:
            merged["peer_group_name"] = merged["peer_group_name"].fillna(
                merged["peer_group_name_meta"]
            )
            merged = merged.drop(columns=["peer_group_name_meta"])
        else:
            merged = merged.rename(columns={"peer_group_name_meta": "peer_group_name"})
    rows = []
    for peer_group, group_df in merged.groupby("peer_group_name"):
        if peer_group in (None, "", "No peer group assigned"):
            continue
        for metric in METRICS:
            if metric not in group_df.columns:
                continue
            values = group_df[metric]
            if values.dropna().empty:
                continue
            ranks = percent_rank(values.fillna(values.min() if values.min() is not None else 0))
            if metric == "debt_to_equity":
                ranks = 1.0 - ranks
            for company_id, value, rank in zip(group_df["company_id"], values, ranks):
                rows.append(
                    {
                        "company_id": company_id,
                        "peer_group_name": peer_group,
                        "metric": metric,
                        "value": value,
                        "percentile_rank": rank,
                        "year": group_df.loc[group_df["company_id"] == company_id, "year"].iloc[0],
                    }
                )
    return pd.DataFrame(rows)


def write_peer_percentiles(df: pd.DataFrame):
    engine = create_engine(f"sqlite:///{DB}")
    df.to_sql("peer_percentiles", engine, if_exists="replace", index=False)
    return df
