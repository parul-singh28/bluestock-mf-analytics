"""Peer endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/peers", tags=["peers"])


@router.get("/{group_name}")
def peers(group_name: str):
    return {"group_name": group_name, "companies": []}
