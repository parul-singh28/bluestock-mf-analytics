from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import get_companies, get_valuation

def build_valuation_outputs(output_dir: str | Path = "output") -> pd.DataFrame:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    companies_df = get_companies()
    rows = []
    sector_pe_values = {}

    for _, company in companies_df.iterrows():
        valuation = get_valuation(company["ticker"])
        if not valuation:
            continue
        if pd.notna(valuation["pe"]):
            sector_pe_values.setdefault(valuation["sector"], []).append(valuation["pe"])

    sector_medians = {sector: pd.Series(values).median() for sector, values in sector_pe_values.items()}

    for _, company in companies_df.iterrows():
        valuation = get_valuation(company["ticker"])
        if not valuation:
            continue
        sector = valuation["sector"]
        sector_median = sector_medians.get(sector)
        pe = valuation["pe"]

        if pd.notna(sector_median) and sector_median > 0:
            pe_vs_sector_median_pct = round(((pe / sector_median) - 1) * 100, 2)
            if pe > sector_median * 1.5:
                flag = "Caution"
            elif pe < sector_median * 0.7:
                flag = "Discount"
            else:
                flag = "Fair"
        else:
            pe_vs_sector_median_pct = None
            flag = "Fair"

        rows.append({
            "company_id": valuation["company_id"],
            "company_name": valuation["company_name"],
            "sector": sector,
            "P/E": pe,
            "P/B": valuation["pb"],
            "EV/EBITDA": valuation["ev_ebitda"],
            "FCF_yield_pct": valuation["fcf_yield_pct"],
            "5yr_median_PE": valuation["five_year_median_pe"],
            "PE_vs_sector_median_pct": pe_vs_sector_median_pct,
            "flag": flag,
        })

    df = pd.DataFrame(rows)
    df.to_excel(output_path / "valuation_summary.xlsx", index=False)
    flags_df = df[df["flag"].isin(["Caution", "Discount"])].copy()
    flags_df.to_csv(output_path / "valuation_flags.csv", index=False)
    return df


if __name__ == "__main__":
    result = build_valuation_outputs(PROJECT_ROOT / "output")
    print(f"Wrote valuation outputs for {len(result)} companies.")
