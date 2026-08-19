"""Valuation endpoints."""
from fastapi import APIRouter

router = APIRouter(tags=["valuation"])


@router.get("/market-cap/{ticker}")
def market_cap(ticker: str):
    return {"ticker": ticker.upper(), "history": []}
