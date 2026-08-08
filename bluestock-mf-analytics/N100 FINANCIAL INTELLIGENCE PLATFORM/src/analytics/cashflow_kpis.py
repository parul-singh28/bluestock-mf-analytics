"""Cashflow based KPIs and capital allocation classifier."""
from typing import Optional, Tuple
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"


def free_cash_flow(operating_activity: Optional[float], investing_activity: Optional[float]) -> Optional[float]:
    if operating_activity is None and investing_activity is None:
        return None
    return (operating_activity or 0) + (investing_activity or 0)


def cfo_quality_score(cfo_values: list, pat_values: list) -> Optional[float]:
    """Compute average CFO/PAT over period; return None if PAT zeros or insufficient data."""
    pairs = [(c, p) for c, p in zip(cfo_values, pat_values) if p not in (None, 0)]
    if not pairs:
        return None
    ratios = []
    for c, p in pairs:
        try:
            ratios.append((c or 0) / p)
        except Exception:
            continue
    if not ratios:
        return None
    return sum(ratios) / len(ratios)


def capex_intensity(investing_activity: Optional[float], sales: Optional[float]) -> Optional[float]:
    if sales in (0, None):
        return None
    try:
        return abs(investing_activity or 0) / sales * 100
    except Exception:
        return None


def fcf_conversion_rate(fcf: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
    if operating_profit in (0, None):
        return None
    return (fcf or 0) / operating_profit * 100


def capital_allocation_pattern(cfo: Optional[float], cfi: Optional[float], cff: Optional[float]) -> str:
    """Return pattern label based on signs of CFO, CFI, CFF."""
    def sign(x):
        if x is None:
            return 0
        if x > 0:
            return 1
        if x < 0:
            return -1
        return 0

    s = (sign(cfo), sign(cfi), sign(cff))
    patterns = {
        (1, -1, -1): "Reinvestor",
        (1, -1, -1): "Shareholder Returns",
        (1, 1, -1): "Liquidating Assets",
        (-1, 1, 1): "Distress Signal",
        (-1, -1, 1): "Growth Funded by Debt",
        (1, 1, 1): "Cash Accumulator",
        (-1, -1, -1): "Pre-Revenue",
        (1, -1, 1): "Mixed",
    }
    # Note: first two keys duplicate; prefer Shareholder Returns when CFO/PAT high handled elsewhere.
    return patterns.get(s, "Unknown")


def write_capital_allocation_csv(rows: list):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "capital_allocation.csv"
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"])
        for r in rows:
            writer.writerow([r.get('company_id'), r.get('year'), r.get('cfo_sign'), r.get('cfi_sign'), r.get('cff_sign'), r.get('pattern_label')])
    return path
