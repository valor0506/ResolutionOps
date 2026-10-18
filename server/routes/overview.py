from fastapi import APIRouter
from server.db.store import store

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/metrics")
async def get_overview_metrics():
    """Retrieve computed dashboard metrics and case status distribution."""
    return store.get_overview_metrics()
