"""Screener filter engine for financial_ratio-based screening."""
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "screener_config.yaml"
OUTPUT = ROOT / "output"


FILTERS = [
    "roe_min",
    "de_max",
    "fcf_min",
    "revenue_cagr_5yr_min",
    "pat_cagr_5yr_min",
    "opm_min",
    "pe_max",
    "pb_max",
    "dividend_yield_min",
    "icr_min",
    "market_cap_min",
    "net_profit_min",
    "eps_cagr_min",
    "asset_turnover_min",
    "sales_min",
]


class ScreenerEngine:
    COLUMN_ALIASES = {
        "fcf": "free_cash_flow",
        "opm": "net_profit_margin_pct",
        "icr": "interest_coverage",
        "sales": "revenue",
    }

    def __init__(self, config_path: Path = None):
        self.config_path = config_path or CONFIG
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Missing screener config: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def apply_filters(self, df: pd.DataFrame, preset: str, company_metadata: pd.DataFrame = None) -> pd.DataFrame:
        preset_filters = self.config.get("presets", {}).get(preset, {})
        if not preset_filters:
            raise ValueError(f"Unknown preset: {preset}")

        df = df.copy()
        if company_metadata is not None and "company_id" in company_metadata.columns:
            df = df.merge(company_metadata[["company_id", "broad_sector"]], on="company_id", how="left")

        composite_scores = []
        for _, row in df.iterrows():
            score = 0.0
            if row.get("composite_quality_score") is not None:
                score = row["composite_quality_score"]
            composite_scores.append(score)
        df["composite_quality_score"] = composite_scores

        for key, threshold in preset_filters.items():
            if key == "de_max":
                if "broad_sector" in df.columns:
                    financials = df["broad_sector"] == "Financials"
                    non_financials = ~financials
                    valid_non_financials = non_financials & (df["debt_to_equity"].fillna(float("inf")) <= threshold)
                    df = df[financials | valid_non_financials]
                else:
                    df = df[df["debt_to_equity"].fillna(float("inf")) <= threshold]
            elif key == "icr_min":
                icr_ok = df["interest_coverage"].fillna(float("inf")) >= threshold
                if "icr_label" in df.columns:
                    icr_ok = icr_ok | (df["interest_coverage"].isna() & (df["icr_label"] == "Debt Free"))
                df = df[icr_ok]
            else:
                column = key.replace("_min", "").replace("_max", "")
                column = self.COLUMN_ALIASES.get(column, column)
                if key.endswith("_min"):
                    df = df[df[column].fillna(-float("inf")) >= threshold]
                elif key.endswith("_max"):
                    df = df[df[column].fillna(float("inf")) <= threshold]
        df = df.sort_values("composite_quality_score", ascending=False)
        return df

    def run_preset(self, df: pd.DataFrame, preset: str, company_metadata: pd.DataFrame = None) -> pd.DataFrame:
        return self.apply_filters(df, preset, company_metadata)
