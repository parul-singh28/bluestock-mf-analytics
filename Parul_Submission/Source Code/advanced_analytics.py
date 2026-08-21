from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def _get_input_paths() -> dict[str, Path]:
    return {
        "fund_master": DATA_DIR / "01_fund_master.csv",
        "nav_history": PROCESSED_DIR / "nav_history_clean.csv",
        "transactions": PROCESSED_DIR / "investor_transactions_clean.csv",
        "performance": PROCESSED_DIR / "scheme_performance_clean.csv",
    }


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fund_master = pd.read_csv(_get_input_paths()["fund_master"])
    nav_history = pd.read_csv(_get_input_paths()["nav_history"])
    transactions = pd.read_csv(_get_input_paths()["transactions"])
    performance = pd.read_csv(_get_input_paths()["performance"])

    fund_master["amfi_code"] = fund_master["amfi_code"].astype(str)
    nav_history["amfi_code"] = nav_history["amfi_code"].astype(str)
    transactions["amfi_code"] = transactions["amfi_code"].astype(str)
    performance["amfi_code"] = performance["amfi_code"].astype(str)

    nav_history["date"] = pd.to_datetime(nav_history["date"], errors="coerce")
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce")

    transactions["transaction_type"] = transactions["transaction_type"].astype(str).str.strip().str.upper()
    transactions["kyc_status"] = transactions["kyc_status"].astype(str).str.strip().str.capitalize()

    return fund_master, nav_history, transactions, performance


def _derive_risk_grade(risk_category: str) -> str:
    mapping = {
        "low": "Low",
        "moderate": "Moderate",
        "medium": "Moderate",
        "high": "High",
        "very high": "High",
        "very-high": "High",
    }
    key = str(risk_category).strip().lower()
    return mapping.get(key, "Moderate")


def compute_var_cvar(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> pd.DataFrame:
    merged = fund_master[["amfi_code", "scheme_name", "fund_house", "risk_category"]].merge(
        nav_history, on="amfi_code", how="left"
    )
    merged = merged.sort_values(["amfi_code", "date"])

    rows: list[dict[str, object]] = []
    for amfi_code, group in merged.groupby("amfi_code"):
        if group["nav"].dropna().nunique() < 2:
            continue
        returns = group["nav"].pct_change().dropna()
        if returns.empty:
            continue
        var_95 = float(returns.quantile(0.05))
        cvar_95 = float(returns[returns <= var_95].mean()) if (returns <= var_95).any() else np.nan
        rows.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": fund_master.loc[fund_master["amfi_code"] == amfi_code, "scheme_name"].iloc[0],
                "fund_house": fund_master.loc[fund_master["amfi_code"] == amfi_code, "fund_house"].iloc[0],
                "risk_category": fund_master.loc[fund_master["amfi_code"] == amfi_code, "risk_category"].iloc[0],
                "risk_grade": _derive_risk_grade(
                    fund_master.loc[fund_master["amfi_code"] == amfi_code, "risk_category"].iloc[0]
                ),
                "var_95_pct": var_95,
                "cvar_95_pct": cvar_95,
                "obs_count": int(returns.shape[0]),
            }
        )

    report = pd.DataFrame(rows)
    if report.empty:
        return report
    report = report.sort_values("var_95_pct", ascending=False)
    return report.reset_index(drop=True)


def plot_rolling_sharpe(fund_master: pd.DataFrame, nav_history: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    merged = fund_master[["amfi_code", "scheme_name"]].merge(nav_history, on="amfi_code", how="left")
    merged = merged.sort_values(["amfi_code", "date"])

    key_funds = merged["amfi_code"].dropna().astype(str).unique().tolist()
    if len(key_funds) > 5:
        key_funds = key_funds[:5]

    wide = []
    for amfi_code in key_funds:
        fund_series = merged.loc[merged["amfi_code"] == amfi_code].copy()
        fund_series = fund_series.sort_values("date")
        if fund_series["nav"].dropna().nunique() < 2:
            continue
        returns = fund_series["nav"].pct_change().dropna()
        window = min(90, len(returns))
        sharpe = returns.rolling(window=window, min_periods=1).mean() / returns.rolling(window=window, min_periods=1).std()
        sharpe = sharpe * np.sqrt(252)
        sharpe = sharpe.replace([np.inf, -np.inf], np.nan)
        sharpe = sharpe.to_frame("rolling_sharpe")
        sharpe["date"] = fund_series["date"].iloc[1:]
        sharpe["amfi_code"] = amfi_code
        wide.append(sharpe)

    if not wide:
        return pd.DataFrame(columns=["date", "amfi_code", "rolling_sharpe"])

    sharpe_df = pd.concat(wide, ignore_index=True)
    sharpe_df = sharpe_df.dropna(subset=["rolling_sharpe"])

    plt.figure(figsize=(10, 5))
    for amfi_code, group in sharpe_df.groupby("amfi_code"):
        scheme_name = fund_master.loc[fund_master["amfi_code"] == amfi_code, "scheme_name"].iloc[0]
        plt.plot(group["date"], group["rolling_sharpe"], label=scheme_name)
    plt.title("Rolling 90-Day Sharpe Ratio")
    plt.xlabel("Date")
    plt.ylabel("Sharpe Ratio")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return sharpe_df


def analyze_investor_cohorts(fund_master: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
    tx = transactions.copy()
    tx["transaction_type"] = tx["transaction_type"].astype(str).str.strip().str.upper()
    tx["amount_inr"] = pd.to_numeric(tx["amount_inr"], errors="coerce")
    tx = tx.dropna(subset=["transaction_date", "amount_inr"])

    first_tx = (
        tx.groupby("investor_id", as_index=False)
        .agg(first_transaction_date=("transaction_date", "min"))
    )
    first_tx["cohort_year"] = first_tx["first_transaction_date"].dt.year

    sip_tx = tx[tx["transaction_type"] == "SIP"].copy()
    sip_tx = sip_tx.groupby(["investor_id", "amfi_code"], as_index=False).agg(
        sip_amount=("amount_inr", "sum"),
        sip_transactions=("amount_inr", "size"),
    )

    invested = (
        tx[tx["transaction_type"] != "REDEMPTION"]
        .groupby("investor_id", as_index=False)
        .agg(total_invested=("amount_inr", "sum"))
    )

    cohort_stats = first_tx.merge(invested, on="investor_id", how="left")
    cohort_stats = cohort_stats.merge(
        sip_tx.groupby("investor_id", as_index=False).agg(avg_sip_amount=("sip_amount", "mean")),
        on="investor_id",
        how="left",
    )

    fund_pref = tx.groupby(["investor_id", "amfi_code"], as_index=False).size()
    fund_pref = fund_pref.sort_values(["investor_id", "size"], ascending=[True, False])
    fund_pref = fund_pref.drop_duplicates("investor_id")
    fund_pref = fund_pref.rename(columns={"amfi_code": "top_fund", "size": "top_fund_transaction_count"})
    cohort_stats = cohort_stats.merge(fund_pref[["investor_id", "top_fund", "top_fund_transaction_count"]], on="investor_id", how="left")

    cohort_stats["avg_sip_amount"] = cohort_stats["avg_sip_amount"].fillna(0)
    cohort_stats["total_invested"] = cohort_stats["total_invested"].fillna(0)
    return cohort_stats.sort_values(["cohort_year", "total_invested"], ascending=[True, False])


def analyze_sip_continuity(transactions: pd.DataFrame) -> pd.DataFrame:
    tx = transactions.copy()
    tx["transaction_type"] = tx["transaction_type"].astype(str).str.strip().str.upper()
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"], errors="coerce")
    tx = tx.dropna(subset=["transaction_date"])
    sip_tx = tx[tx["transaction_type"] == "SIP"].copy()

    rows = []
    for investor_id, group in sip_tx.groupby("investor_id"):
        group = group.sort_values("transaction_date")
        if len(group) < 6:
            continue
        gaps = group["transaction_date"].diff().dropna().dt.days
        avg_gap = float(gaps.mean()) if not gaps.empty else np.nan
        max_gap = float(gaps.max()) if not gaps.empty else np.nan
        rows.append(
            {
                "investor_id": investor_id,
                "sip_transaction_count": int(len(group)),
                "avg_gap_days": avg_gap,
                "max_gap_days": max_gap,
                "at_risk": bool((avg_gap > 35) or (max_gap > 35)),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=["investor_id", "sip_transaction_count", "avg_gap_days", "max_gap_days", "at_risk"]
        )
    return pd.DataFrame(rows).sort_values("avg_gap_days", ascending=False)


def compute_sector_hhi(fund_master: pd.DataFrame) -> pd.DataFrame:
    sector_weights = []
    for sub_category in fund_master["sub_category"].astype(str):
        if sub_category.lower() == "large cap":
            weights = {"Financials": 0.30, "Technology": 0.25, "Consumer": 0.20, "Healthcare": 0.15, "Energy": 0.10}
        elif sub_category.lower() == "mid cap":
            weights = {"Financials": 0.25, "Technology": 0.20, "Consumer": 0.20, "Industrials": 0.20, "Healthcare": 0.15}
        else:
            weights = {"Financials": 0.25, "Technology": 0.25, "Consumer": 0.25, "Industrials": 0.25}
        sector_weights.append(weights)

    result = fund_master[["amfi_code", "scheme_name", "sub_category"]].copy()
    result["hhi"] = [sum(weight**2 for weight in weights.values()) for weights in sector_weights]
    result["concentration_label"] = np.where(result["hhi"] >= 0.35, "High", "Moderate")
    return result.sort_values("hhi", ascending=False).reset_index(drop=True)


def recommend_funds(risk_appetite: str, fund_master: pd.DataFrame, performance: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    risk_appetite = str(risk_appetite).strip().capitalize()
    desired_risk = {"Low": "Low", "Moderate": "Moderate", "Medium": "Moderate", "High": "High"}.get(risk_appetite, risk_appetite)

    merged = fund_master[["amfi_code", "scheme_name", "fund_house", "risk_category"]].merge(
        performance, on="amfi_code", how="left"
    )
    merged["risk_grade"] = merged["risk_category"].apply(_derive_risk_grade)
    filtered = merged[merged["risk_grade"] == desired_risk].copy()
    if filtered.empty:
        filtered = merged[merged["risk_grade"].isin([desired_risk, "Moderate", "High"])]
    filtered = filtered.sort_values(["sharpe_ratio", "return_3yr_pct"], ascending=[False, False])
    return filtered.head(top_n).reset_index(drop=True)


def export_outputs() -> dict[str, Path]:
    fund_master, nav_history, transactions, performance = load_data()
    var_report = compute_var_cvar(fund_master, nav_history)
    var_report.to_csv(PROJECT_ROOT / "var_cvar_report.csv", index=False)
    sharpe_chart = plot_rolling_sharpe(fund_master, nav_history, PROJECT_ROOT / "rolling_sharpe_chart.png")
    cohort_report = analyze_investor_cohorts(fund_master, transactions)
    cohort_report.to_csv(PROJECT_ROOT / "cohort_report.csv", index=False)
    sip_continuity = analyze_sip_continuity(transactions)
    sip_continuity.to_csv(PROJECT_ROOT / "sip_continuity.csv", index=False)
    hhi_report = compute_sector_hhi(fund_master)
    hhi_report.to_csv(PROJECT_ROOT / "hhi_report.csv", index=False)
    return {
        "var_report": PROJECT_ROOT / "var_cvar_report.csv",
        "sharpe_chart": PROJECT_ROOT / "rolling_sharpe_chart.png",
        "cohort_report": PROJECT_ROOT / "cohort_report.csv",
        "sip_continuity": PROJECT_ROOT / "sip_continuity.csv",
        "hhi_report": PROJECT_ROOT / "hhi_report.csv",
        "var_report_df": var_report,
        "sharpe_chart_df": sharpe_chart,
        "cohort_report_df": cohort_report,
        "sip_continuity_df": sip_continuity,
        "hhi_report_df": hhi_report,
    }


def main() -> None:
    outputs = export_outputs()
    print("Created", outputs["var_report"])
    print("Created", outputs["sharpe_chart"])
    print("Created", PROJECT_ROOT / "cohort_report.csv")
    print("Created", PROJECT_ROOT / "sip_continuity.csv")
    print("Created", PROJECT_ROOT / "hhi_report.csv")


if __name__ == "__main__":
    main()
