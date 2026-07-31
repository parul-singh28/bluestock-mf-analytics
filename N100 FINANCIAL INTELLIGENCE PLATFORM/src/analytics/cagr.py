"""CAGR engine with edge-case flags."""
from typing import Optional, Tuple, List
import math


class CAGRFlag:
    DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
    TURNAROUND = "TURNAROUND"
    BOTH_NEGATIVE = "BOTH_NEGATIVE"
    ZERO_BASE = "ZERO_BASE"
    INSUFFICIENT = "INSUFFICIENT"


def compute_cagr(start: float, end: float, n: int) -> Tuple[Optional[float], Optional[str]]:
    """Compute CAGR in percent and return (value_pct, flag).
    Flags handle edge cases per spec.
    """
    if n <= 0:
        return None, CAGRFlag.INSUFFICIENT
    if start is None or end is None:
        return None, CAGRFlag.INSUFFICIENT
    try:
        if start == 0:
            return None, CAGRFlag.ZERO_BASE
        if start > 0 and end > 0:
            val = (end / start) ** (1 / n) - 1
            return val * 100, None
        if start > 0 and end < 0:
            return None, CAGRFlag.DECLINE_TO_LOSS
        if start < 0 and end > 0:
            return None, CAGRFlag.TURNAROUND
        if start < 0 and end < 0:
            return None, CAGRFlag.BOTH_NEGATIVE
    except Exception:
        return None, CAGRFlag.INSUFFICIENT


def cagr_from_series(values: List[float], years: List[int], window: int) -> Tuple[Optional[float], Optional[str]]:
    """Given a list of values and their years (ascending), compute CAGR over last `window` years.
    Returns (cagr_pct, flag).
    """
    if len(values) < 2:
        return None, CAGRFlag.INSUFFICIENT
    # assume years sorted ascending
    end_year = years[-1]
    start_year = end_year - window
    # find start index with year <= start_year (closest >=?) require exact n years? We'll require presence of start year value exactly window years before
    target_start_year = end_year - window
    # find first value with year == target_start_year
    if target_start_year not in years:
        return None, CAGRFlag.INSUFFICIENT
    start_idx = years.index(target_start_year)
    end_idx = len(years) - 1
    n = window
    start_val = values[start_idx]
    end_val = values[end_idx]
    return compute_cagr(start_val, end_val, n)
