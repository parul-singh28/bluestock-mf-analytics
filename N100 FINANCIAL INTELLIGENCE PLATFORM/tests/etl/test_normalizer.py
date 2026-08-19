import pytest
from src.etl.normaliser import normalize_year, normalize_ticker


def test_normalize_year_full_4digit():
    assert normalize_year("2020") == 2020


@pytest.mark.parametrize("inp,expected", [
    ("FY20", 2020),
    ("'20", 2020),
    ("20", 2020),
    ("FY1999", 1999),
    ("99", 1999),
    ("00", 2000),
    ("49", 2049),
    ("50", 1950),
    ("FY05", 2005),
    ("2018", 2018),
    ("  2017 ", 2017),
    ("FY-21", 2021),
    ("'99", 1999),
    (None, None),
    ("n/a", None),
    ("FY21", 2021),
    ("202", 202),
    ("abc2021xyz", 2021),
    ("FY 03", 2003),
    ("03", 2003),
])
def test_normalize_year_various(inp, expected):
    assert normalize_year(inp) == expected


@pytest.mark.parametrize("inp,expected", [
    ("tcs.nse", "TCS"),
    ("tata_steel", "TATASTEEL"),
    (" infy ", "INFY"),
    ("reliance.NSE", "RELIANCE"),
    ("sbilife", "SBILIFE"),
    ("abc-xyz", "ABCXYZ"),
    (None, None),
    ("1234.ns", "1234"),
    ("ABCD/EX", "ABCD"),
    ("a.b-c:d_e", "ABCDE"),
    ("TCS", "TCS"),
    ("tcs.nse.in", "TCS"),
    ("t-cs", "TCS"),
    ("tcs#1", "TCS1"),
    ("tcs@nse", "TCS"),
])
def test_normalize_ticker_various(inp, expected):
    assert normalize_ticker(inp) == expected


def test_normalize_ticker_removes_specials():
    assert normalize_ticker("a b.c-d/e_f") == "ABCDEF"


# Ensure at least 35 tests -- add some boundary cases
def test_year_two_digit_upper_bound():
    assert normalize_year("49") == 2049


def test_year_two_digit_lower_bound():
    assert normalize_year("50") == 1950


def test_ticker_empty_string():
    assert normalize_ticker("") == ""
