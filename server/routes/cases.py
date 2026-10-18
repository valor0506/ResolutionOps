from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from server.db.store import store
from server.models.schemas import (
    Case,
    CaseCreateRequest,
    CaseUpdateRequest,
    EvidenceRecord,
    AddEvidenceRequest,
    DiagnosticHypothesis,
    HypothesisStatus,
    EngineeringHandoff,
    VerificationResult,
    AuditRecord,
)

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=dict)
async def list_cases(
    search: Optional[str] = Query(None, description="Search query across ID, title, customer, summary"),
    status: Optional[str] = Query(None, description="Filter by CaseStatus enum value"),
    priority: Optional[str] = Query(None, description="Filter by CasePriority enum value"),
    customer_id: Optional[str] = Query(None, description="Filter by Customer ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Search and filter customer issue cases."""
    cases, total = store.list_cases(
        search=search,
        status=status,
        priority=priority,
        customer_id=customer_id,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [c.model_dump(mode="json") for c in cases],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{case_id}", response_model=Case)
async def get_case(case_id: str):
    """Retrieve complete case details."""
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return case


@router.post("", response_model=Case, status_code=status.HTTP_201_CREATED)
async def create_case(req: CaseCreateRequest):
    """Create a new validated support case."""
    try:
        new_case = store.create_case(req)
        return new_case
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{case_id}", response_model=Case)
async def update_case(case_id: str, req: CaseUpdateRequest):
    """Update case status, owner, blocker, or resolution details with verification gates."""
    try:
        updated = store.update_case(case_id, req)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))


# ============================================================================
# Evidence Timeline
# ============================================================================

@router.get("/{case_id}/evidence", response_model=List[EvidenceRecord])
async def get_case_evidence(case_id: str):
    """Retrieve timestamped evidence records for a case."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return store.get_case_evidence(case_id)


@router.post("/{case_id}/evidence", response_model=EvidenceRecord, status_code=status.HTTP_201_CREATED)
async def add_case_evidence(case_id: str, req: AddEvidenceRequest):
    """Add a new evidence record or internal note to the case timeline."""
    try:
        record = store.add_case_evidence(case_id, req)
        return record
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")


# ============================================================================
# Diagnostic Hypotheses
# ============================================================================

@router.get("/{case_id}/hypotheses", response_model=List[DiagnosticHypothesis])
async def get_case_hypotheses(case_id: str):
    """Retrieve ranked diagnostic hypotheses for a case."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return store.get_case_hypotheses(case_id)


@router.patch("/{case_id}/hypotheses/{hypothesis_id}", response_model=DiagnosticHypothesis)
async def update_hypothesis_status(case_id: str, hypothesis_id: str, status_val: HypothesisStatus):
    """Accept, reject, or mark a hypothesis as under active investigation."""
    updated = store.update_hypothesis_status(case_id, hypothesis_id, status_val)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hypothesis '{hypothesis_id}' not found in case '{case_id}'",
        )
    return updated


# ============================================================================
# Engineering Handoff
# ============================================================================

@router.get("/{case_id}/handoff", response_model=Optional[EngineeringHandoff])
async def get_case_handoff(case_id: str):
    """Retrieve the engineering handoff document for a case."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    handoff = store.get_case_handoff(case_id)
    return handoff


@router.put("/{case_id}/handoff", response_model=EngineeringHandoff)
async def save_case_handoff(case_id: str, handoff: EngineeringHandoff):
    """Save or update an engineering handoff package."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return store.save_case_handoff(case_id, handoff)


# ============================================================================
# Verification Checklist
# ============================================================================

@router.get("/{case_id}/verification", response_model=Optional[VerificationResult])
async def get_case_verification(case_id: str):
    """Retrieve the verification checklist and status for a case."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return store.get_case_verification(case_id)


@router.put("/{case_id}/verification", response_model=VerificationResult)
async def update_case_verification(case_id: str, verification: VerificationResult):
    """Update verification test criteria results and closure authorization."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return store.update_case_verification(case_id, verification)


# ============================================================================
# Audit Trail
# ============================================================================

@router.get("/{case_id}/audit", response_model=List[AuditRecord])
async def get_case_audit_trail(case_id: str):
    """Retrieve auditable history of state changes and approvals for a case."""
    if not store.get_case(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found")
    return store.get_case_audit_trail(case_id)
