from fastapi import APIRouter, HTTPException, status
from server.ai.client import gemini_manager
from server.ai.extractor import parse_unstructured_intake
from server.ai.investigator import run_investigation_hypotheses
from server.ai.handoff import generate_engineering_handoff, draft_customer_response
from server.db.store import store
from server.models.schemas import (
    IntakeParseRequest,
    IntakeParseResponse,
    EngineeringHandoff,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
async def get_ai_status():
    """Returns AI model provider availability status and active mode."""
    return {
        "gemini_available": gemini_manager.is_available,
        "model": "gemini-2.5-flash" if gemini_manager.is_available else "deterministic-grounded-fallback",
        "provider": "Google Gen AI SDK",
        "status": "ready",
    }


@router.post("/intake-parse", response_model=IntakeParseResponse)
async def intake_parse(req: IntakeParseRequest):
    """Convert an unstructured customer complaint into a validated structured issue report."""
    if not req.unstructured_complaint.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unstructured_complaint must not be empty",
        )
    return await parse_unstructured_intake(req.unstructured_complaint, req.customer_id)


@router.post("/cases/{case_id}/investigate")
async def investigate_case(case_id: str):
    """Run root-cause investigation on unified case evidence, generating ranked hypotheses."""
    if not store.get_case(case_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found",
        )
    hypotheses = await run_investigation_hypotheses(case_id)
    store.set_case_hypotheses(case_id, hypotheses, author="Gemini Reliability Investigator")
    return {"case_id": case_id, "hypotheses": [h.model_dump(mode="json") for h in hypotheses]}


@router.post("/cases/{case_id}/generate-handoff", response_model=EngineeringHandoff)
async def create_handoff(case_id: str):
    """Generate or refresh an engineering handoff dossier for an escalated case."""
    try:
        handoff = generate_engineering_handoff(case_id)
        return handoff
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found",
        )


@router.get("/cases/{case_id}/customer-response")
async def get_customer_response_draft(case_id: str):
    """Draft an evidence-grounded customer update explaining findings without false claims."""
    try:
        draft = draft_customer_response(case_id)
        return {"case_id": case_id, "draft": draft}
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found",
        )
