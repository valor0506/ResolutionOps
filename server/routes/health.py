from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check — confirms the API server is running."""
    return {"status": "ok", "service": "resolutionops-api"}
