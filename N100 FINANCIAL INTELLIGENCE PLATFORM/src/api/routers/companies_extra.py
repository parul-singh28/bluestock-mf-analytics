"""Additional company route helpers."""
from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/{ticker}/ratios")
def ratios(ticker: str):
    return {"ticker": ticker.upper(), "history": []}


@router.get("/{ticker}/tearsheet")
def tearsheet(ticker: str):
    return {"ticker": ticker.upper(), "status": "not-found"}
