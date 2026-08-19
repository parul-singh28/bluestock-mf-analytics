"""Document endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["documents"])


@router.get("/{ticker}/documents")
def documents(ticker: str):
    return {"ticker": ticker.upper(), "documents": []}
