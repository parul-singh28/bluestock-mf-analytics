from datetime import datetime
import re


def normalize_year(value):
    """Normalize various year representations to integer year (e.g., 'FY20', '2020', "'20")"""
    if value is None:
        return None
    s = str(value).strip()
    # common patterns: FY2020, FY20, '20, 2020, 20
    s = s.upper()
    s = s.replace("FY", "")
    s = s.replace("'", "")
    s = s.replace("\u2019", "")
    # Remove non-digit prefix/suffix
    m = re.search(r"(\d{2,4})", s)
    if not m:
        return None
    year_part = m.group(1)
    if len(year_part) == 2:
        # interpret 00-49 as 2000-2049, 50-99 as 1950-1999
        y = int(year_part)
        if y <= 49:
            return 2000 + y
        else:
            return 1900 + y
    return int(year_part)


def normalize_ticker(ticker):
    """Normalize stock tickers to uppercase, remove exchange suffixes and whitespace.

    Examples: 'tcs.nse' -> 'TCS', 'tata_steel' -> 'TATASTEEL'
    """
    if ticker is None:
        return None
    s = str(ticker).strip().upper()
    # remove common exchange suffixes
    s = re.split(r"[\.\-_/:]", s)[0]
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s
