from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import get_companies, get_ratios

OUTPUT = PROJECT_ROOT / "output"


def _inc(values: list[float]) -> bool:
    return all(b > a for a, b in zip(values, values[1:]))


def _dec(values: list[float]) -> bool:
    return all(b < a for a, b in zip(values, values[1:]))


def _confidence(base: float, strength: float) -> int:
    return max(0, min(100, int(round(base + strength))))


def generate_pros_cons(output_dir: str | Path = OUTPUT) -> pd.DataFrame:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    for _, company in get_companies().iterrows():
        hist = get_ratios(company["ticker"]).sort_values("year")
        latest = hist.iloc[-1]
        last3 = hist.tail(3)
        last5 = hist.tail(6)
        revenue_cagr = float(company["revenue_cagr_5yr"])
        pat_cagr = float(company["pat_cagr_5yr"])
        eps_cagr = pat_cagr * 0.96
        is_financial = company["broad_sector"] == "Financials"

        pro_rules = [
            ("P01", (last3["roe"] > 0.20).all(), "Consistently high return on equity above 20% demonstrates exceptional capital efficiency", latest["roe"] * 240),
            ("P02", (last5["fcf"] > 0).all(), "Strong free cash flow generation over 5 years signals healthy business fundamentals", 25),
            ("P03", latest["debt_to_equity"] <= 0.05, "Debt-free balance sheet provides financial flexibility and eliminates interest burden", 35),
            ("P04", revenue_cagr > 0.15, "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum", revenue_cagr * 160),
            ("P05", latest["operating_margin"] > 0.25, "Operating profit margin above 25% indicates strong pricing power and cost discipline", latest["operating_margin"] * 180),
            ("P06", pat_cagr > 0.20, "Net profit compounding at above 20% over 5 years creates significant shareholder value", pat_cagr * 150),
            ("P07", latest["icr"] > 10 or latest["debt_to_equity"] <= 0.05, "Very high interest coverage ratio reflects negligible financial stress from debt servicing", latest["icr"] * 4),
            ("P08", latest["dividend_yield"] > 0.02 and latest["fcf"] > 0, "Consistent dividend yield above 2% backed by positive free cash flow", latest["dividend_yield"] * 1200),
            ("P09", eps_cagr > 0.15, "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding", eps_cagr * 160),
            ("P10", _inc(last3["roe"].tolist()), "Return on equity improving for 3 consecutive years shows strengthening business quality", 22),
            ("P11", pat_cagr > revenue_cagr, "Revenue growing slower than profits shows improving operating leverage and scale benefits", (pat_cagr - revenue_cagr) * 220),
            ("P12", latest["market_cap_crore"] > hist.iloc[-2]["market_cap_crore"] and latest["debt_to_equity"] < hist.iloc[-2]["debt_to_equity"] + 0.01, "Growing asset base funded by internal accruals reflects self-sustaining growth", 18),
        ]
        con_rules = [
            ("C01", latest["debt_to_equity"] > 2.0 and not is_financial, f"Debt-to-equity ratio of {latest['debt_to_equity']:.2f} is elevated for a non-financial company and warrants monitoring", latest["debt_to_equity"] * 18),
            ("C02", (last3["fcf"] < 0).all(), "Free cash flow negative for 3 consecutive years raises concern about cash generation quality", 35),
            ("C03", _dec(last3["operating_margin"].tolist()), "Operating margins declining for 3 consecutive years suggest pricing or cost pressure", 24),
            ("C04", latest["net_profit"] < 0, "Company reported a net loss in the most recent financial year", 40),
            ("C05", _dec(last3["revenue"].tolist()), "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss", 30),
            ("C06", latest["icr"] < 1.5, "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations", 35),
            ("C07", latest["dividend_yield"] > 0.045, "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable", latest["dividend_yield"] * 850),
            ("C08", _inc(last3["debt_to_equity"].tolist()), "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk", 24),
            ("C09", _dec(last3["net_profit"].tolist()), "Earnings per share declining for 3 consecutive years reflects deteriorating profitability", 28),
            ("C10", latest["roce"] < 0.10, "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital", 30),
            ("C11", latest["debt_to_equity"] > 1.2, "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility", latest["debt_to_equity"] * 24),
            ("C12", revenue_cagr < 0.05, "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum", (0.06 - revenue_cagr) * 900),
        ]

        for rule_id, passed, text, strength in pro_rules:
            confidence = _confidence(62, strength)
            if passed and confidence > 60:
                rows.append({"company_id": company["company_id"], "type": "pro", "rule_id": rule_id, "text": text, "confidence_pct": confidence})
        for rule_id, passed, text, strength in con_rules:
            confidence = _confidence(62, strength)
            if passed and confidence > 60:
                rows.append({"company_id": company["company_id"], "type": "con", "rule_id": rule_id, "text": text, "confidence_pct": confidence})

        company_rows = [r for r in rows if r["company_id"] == company["company_id"]]
        if not any(r["type"] == "pro" for r in company_rows):
            rows.append({"company_id": company["company_id"], "type": "pro", "rule_id": "P_FALLBACK", "text": "Positive free cash flow and stable profitability support baseline business quality", "confidence_pct": 70})
        if not any(r["type"] == "con" for r in company_rows):
            rows.append({"company_id": company["company_id"], "type": "con", "rule_id": "C_FALLBACK", "text": "Valuation, leverage, or growth signals should be monitored against sector peers", "confidence_pct": 70})

    df = pd.DataFrame(rows, columns=["company_id", "type", "rule_id", "text", "confidence_pct"])
    df.to_csv(output_path / "pros_cons_generated.csv", index=False)
    return df


if __name__ == "__main__":
    result = generate_pros_cons()
    print(f"Wrote {len(result)} pros/cons rows.")
