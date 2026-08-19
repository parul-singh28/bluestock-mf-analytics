"""Sector endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("")
def sectors():
    return []
