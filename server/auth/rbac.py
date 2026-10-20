"""
RBAC (Role-Based Access Control) module for ResolutionOps.

Provides a demo persona switcher that simulates three enterprise roles:
  - support_engineer: Can view cases, run diagnostics, add evidence
  - support_lead: Can do everything a support_engineer can + approve hypotheses, generate handoffs, close cases
  - platform_engineer: Can view all data, run all diagnostics, view audit trails, reset data

In a production deployment, these roles would be enforced via Firebase Auth custom claims
or an external identity provider.  For the demo, the active persona is stored server-side
and switched via a simple API call.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class UserRole(str, Enum):
    SUPPORT_ENGINEER = "support_engineer"
    SUPPORT_LEAD = "support_lead"
    PLATFORM_ENGINEER = "platform_engineer"


# Permissions each role grants
ROLE_PERMISSIONS: Dict[UserRole, List[str]] = {
    UserRole.SUPPORT_ENGINEER: [
        "cases:read",
        "cases:create",
        "cases:update",
        "evidence:read",
        "evidence:create",
        "diagnostics:execute",
        "hypotheses:read",
        "knowledge:read",
        "customers:read",
        "ai:intake",
        "ai:investigate",
        "ai:assistant",
    ],
    UserRole.SUPPORT_LEAD: [
        "cases:read",
        "cases:create",
        "cases:update",
        "cases:resolve",
        "evidence:read",
        "evidence:create",
        "diagnostics:execute",
        "hypotheses:read",
        "hypotheses:approve",
        "handoff:generate",
        "handoff:approve",
        "verification:approve",
        "knowledge:read",
        "customers:read",
        "ai:intake",
        "ai:investigate",
        "ai:assistant",
        "ai:customer-response",
        "audit:read",
    ],
    UserRole.PLATFORM_ENGINEER: [
        "cases:read",
        "cases:create",
        "cases:update",
        "cases:resolve",
        "evidence:read",
        "evidence:create",
        "diagnostics:execute",
        "hypotheses:read",
        "hypotheses:approve",
        "handoff:generate",
        "handoff:approve",
        "verification:approve",
        "knowledge:read",
        "customers:read",
        "ai:intake",
        "ai:investigate",
        "ai:assistant",
        "ai:customer-response",
        "audit:read",
        "system:reset",
        "system:settings",
    ],
}


class DemoPersona(BaseModel):
    id: str
    display_name: str
    email: str
    role: UserRole
    avatar_initials: str
    title: str


# Pre-defined demo personas
DEMO_PERSONAS: List[DemoPersona] = [
    DemoPersona(
        id="user-001",
        display_name="Priya Sharma",
        email="priya.sharma@resolutionops.dev",
        role=UserRole.SUPPORT_ENGINEER,
        avatar_initials="PS",
        title="Support Engineer",
    ),
    DemoPersona(
        id="user-002",
        display_name="Marcus Rivera",
        email="marcus.rivera@resolutionops.dev",
        role=UserRole.SUPPORT_LEAD,
        avatar_initials="MR",
        title="Senior Support Lead",
    ),
    DemoPersona(
        id="user-003",
        display_name="Alex Kim",
        email="alex.kim@resolutionops.dev",
        role=UserRole.PLATFORM_ENGINEER,
        avatar_initials="AK",
        title="Platform Reliability Engineer",
    ),
]


class PersonaManager:
    """Manages the currently active demo persona (server-side singleton)."""

    def __init__(self):
        # Default to Support Lead — the most common demo role
        self._active_persona: DemoPersona = DEMO_PERSONAS[1]

    @property
    def active(self) -> DemoPersona:
        return self._active_persona

    @property
    def permissions(self) -> List[str]:
        return ROLE_PERMISSIONS.get(self._active_persona.role, [])

    def switch(self, persona_id: str) -> Optional[DemoPersona]:
        for p in DEMO_PERSONAS:
            if p.id == persona_id:
                self._active_persona = p
                return p
        return None

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def list_personas(self) -> List[DemoPersona]:
        return DEMO_PERSONAS


# Global singleton
persona_manager = PersonaManager()

