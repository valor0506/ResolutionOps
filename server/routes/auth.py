from fastapi import APIRouter
from server.auth.rbac import persona_manager, ROLE_PERMISSIONS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/personas")
async def list_personas():
    """List all available demo personas for the role switcher."""
    personas = persona_manager.list_personas()
    active = persona_manager.active
    return {
        "personas": [p.model_dump() for p in personas],
        "active_persona_id": active.id,
    }


@router.get("/me")
async def get_current_persona():
    """Returns the currently active demo persona and their permissions."""
    active = persona_manager.active
    return {
        "persona": active.model_dump(),
        "permissions": persona_manager.permissions,
        "role_display": active.role.value.replace("_", " ").title(),
    }


@router.post("/switch/{persona_id}")
async def switch_persona(persona_id: str):
    """Switch the active demo persona. Returns the new persona and permissions."""
    result = persona_manager.switch(persona_id)
    if not result:
        return {"error": f"Persona '{persona_id}' not found"}, 404

    return {
        "persona": result.model_dump(),
        "permissions": persona_manager.permissions,
        "role_display": result.role.value.replace("_", " ").title(),
    }


@router.get("/roles")
async def list_roles():
    """Returns all defined roles and their permission sets."""
    return {
        role.value: {
            "permissions": perms,
            "permission_count": len(perms),
        }
        for role, perms in ROLE_PERMISSIONS.items()
    }

