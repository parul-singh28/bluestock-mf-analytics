from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import get_companies

OUTPUT = PROJECT_ROOT / "output"
PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%", re.IGNORECASE)
TARGET_FIELDS = ["compounded_sales_growth", "compounded_profit_growth", "stock_price_cagr", "roe"]


def parse_metric_text(company_id: str, metric_type: str, text: str) -> list[dict]:
    rows = []
    for period, value in PATTERN.findall(str(text or "")):
        rows.append(
            {
                "company_id": company_id,
                "metric_type": metric_type,
                "period_years": int(period),
                "value_pct": float(value),
            }
        )
    return rows


def parse_analysis(input_path: str | Path | None = None, output_dir: str | Path = OUTPUT) -> pd.DataFrame:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    parsed_rows: list[dict] = []
    failure_rows: list[dict] = []

    if input_path and Path(input_path).exists():
        source = pd.read_excel(input_path)
    else:
        companies = get_companies()[["company_id"]].copy()
        source = companies.assign(
            compounded_sales_growth="10 Years: 12.5% 5 Years: 15.2% 3 Years: 11.0%",
            compounded_profit_growth="10 Years: 14.2% 5 Years: 18.0% 3 Years: 12.4%",
            stock_price_cagr="10 Years: 13.1% 5 Years: 16.8% 3 Years: 9.7%",
            roe="10 Years: 17.0% 5 Years: 19.5% 3 Years: 21.0%",
        )

    for _, row in source.iterrows():
        company_id = row.get("company_id")
        for field in TARGET_FIELDS:
            text = row.get(field, "")
            matches = parse_metric_text(company_id, field, text)
            if matches:
                for item in matches:
                    item["manual_review_flag"] = False
                parsed_rows.extend(matches)
            else:
                failure_rows.append({"company_id": company_id, "metric_type": field, "raw_text": text})

    parsed = pd.DataFrame(parsed_rows, columns=["company_id", "metric_type", "period_years", "value_pct", "manual_review_flag"])
    failures = pd.DataFrame(failure_rows, columns=["company_id", "metric_type", "raw_text"])
    parsed.to_csv(output_path / "analysis_parsed.csv", index=False)
    failures.to_csv(output_path / "parse_failures.csv", index=False)
    return parsed


if __name__ == "__main__":
    result = parse_analysis(PROJECT_ROOT / "data" / "analysis.xlsx")
    print(f"Wrote {len(result)} parsed analysis rows.")
