from fastapi import APIRouter, HTTPException, status
from server.ai.client import gemini_manager
from server.auth.rbac import persona_manager
from server.db.store import DataStore, store as global_store

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/status")
async def get_system_status():
    """Returns full system status: AI provider, persona, data state."""
    active = persona_manager.active
    return {
        "ai": {
            "gemini_available": gemini_manager.is_available,
            "model": "gemini-2.5-flash" if gemini_manager.is_available else "deterministic-grounded-fallback",
            "provider": "Google Gen AI SDK",
            "mode": "live" if gemini_manager.is_available else "deterministic",
        },
        "persona": {
            "id": active.id,
            "display_name": active.display_name,
            "role": active.role.value,
            "title": active.title,
        },
        "data": {
            "total_customers": len(global_store.customers),
            "total_cases": len(global_store.cases),
            "total_knowledge_articles": len(global_store.knowledge_articles),
            "is_demonstration_data": True,
        },
    }


@router.post("/reset-data")
async def reset_synthetic_data():
    """Re-initialize all synthetic data to its original seeded state.
    
    Requires platform_engineer role.
    """
    if not persona_manager.has_permission("system:reset"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{persona_manager.active.role.value}' does not have permission 'system:reset'. Switch to Platform Engineer to reset data.",
        )

    # Re-initialize the store (reloads all seed data)
    global_store.__init__()

    return {
        "success": True,
        "message": "All synthetic data has been reset to its original seeded state.",
        "counts": {
            "customers": len(global_store.customers),
            "cases": len(global_store.cases),
            "knowledge_articles": len(global_store.knowledge_articles),
        },
    }

