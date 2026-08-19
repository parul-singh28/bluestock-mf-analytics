"""Portfolio endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/stats")
def stats():
    return {"statistics": []}
