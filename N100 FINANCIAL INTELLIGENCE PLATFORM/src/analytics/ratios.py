"""Profitability, leverage and efficiency ratio functions."""
from typing import Optional, Tuple

from src.etl.normaliser import normalize_ticker, normalize_year


def safe_div(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    try:
        if numerator is None or denominator is None:
            return None
        if denominator == 0:
            return None
        return numerator / denominator
    except Exception:
        return None


def net_profit_margin_pct(net_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    if sales in (0, None):
        return None
    val = safe_div(net_profit, sales)
    if val is None:
        return None
    return val * 100


def operating_profit_margin_pct(operating_profit: Optional[float], sales: Optional[float], opm_percentage_field: Optional[float] = None) -> Tuple[Optional[float], Optional[float]]:
    """Return computed OPM% and difference against opm_percentage_field (if provided).
    Returns (opm_pct, diff_pct) where diff_pct = abs(opm_pct - opm_percentage_field)
    If sales==0 -> (None, None)
    """
    if sales in (0, None):
        return None, None
    comp = safe_div(operating_profit, sales)
    if comp is None:
        return None, None
    opm_pct = comp * 100
    diff = None
    if opm_percentage_field is not None:
        try:
            diff = abs(opm_pct - float(opm_percentage_field))
        except Exception:
            diff = None
    return opm_pct, diff


def return_on_equity_pct(net_profit: Optional[float], equity: Optional[float], reserves: Optional[float]) -> Optional[float]:
    if equity is None and reserves is None:
        return None
    equity = equity or 0
    reserves = reserves or 0
    if equity < 0 and reserves > 0:
        denom = reserves
    else:
        denom = equity + reserves
    if denom <= 0:
        return None
    val = safe_div(net_profit, denom)
    if val is None:
        return None
    return val * 100


def return_on_capital_employed_pct(ebit: Optional[float], equity: Optional[float], reserves: Optional[float], borrowings: Optional[float], broad_sector: Optional[str] = None, sector_benchmark: Optional[float] = None) -> Tuple[Optional[float], Optional[bool]]:
    """Compute ROCE; returns (roce_pct, benchmark_flag)
    If broad_sector == 'Financials' and sector_benchmark provided, benchmark_flag indicates whether below benchmark.
    """
    equity = (equity or 0)
    reserves = (reserves or 0)
    borrowings = (borrowings or 0)
    if broad_sector and broad_sector.lower() == "financials":
        denom = equity + reserves
    else:
        denom = equity + reserves + borrowings
    if denom == 0:
        return None, None
    val = safe_div(ebit, denom)
    if val is None:
        return None, None
    roce_pct = val * 100
    benchmark_flag = None
    if broad_sector and broad_sector.lower() == "financials" and sector_benchmark is not None:
        try:
            benchmark_flag = roce_pct >= float(sector_benchmark)
        except Exception:
            benchmark_flag = None
    return roce_pct, benchmark_flag


def return_on_assets_pct(net_profit: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    if total_assets in (0, None):
        return None
    val = safe_div(net_profit, total_assets)
    if val is None:
        return None
    return val * 100


def debt_to_equity(borrowings: Optional[float], equity: Optional[float], reserves: Optional[float]) -> Optional[float]:
    if borrowings in (None, 0):
        return 0.0 if borrowings == 0 else None
    equity = equity or 0
    reserves = reserves or 0
    denom = equity + reserves
    if denom == 0:
        return None
    return safe_div(borrowings, denom)


def interest_coverage(operating_profit: Optional[float], other_income: Optional[float], interest: Optional[float]) -> Optional[float]:
    if interest in (0, None):
        return None
    num = (operating_profit or 0) + (other_income or 0)
    return safe_div(num, interest)


def net_debt(borrowings: Optional[float], investments: Optional[float]) -> Optional[float]:
    if borrowings is None and investments is None:
        return None
    borrowings = borrowings or 0
    investments = investments or 0
    return borrowings - investments


def asset_turnover(sales: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    if total_assets in (0, None):
        return None
    return safe_div(sales, total_assets)
