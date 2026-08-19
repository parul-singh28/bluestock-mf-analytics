"""Screener endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/screener", tags=["screener"])


@router.get("")
def screener():
    return []
