import json
from fastapi import APIRouter, HTTPException, status

from server.db.store import store
from server.models.schemas import (
    DiagnosticToolExecutionRequest,
    DiagnosticToolExecutionResponse,
    AddEvidenceRequest,
    EvidenceSource,
    EvidenceType,
)
from server.services.diagnostic_tools import execute_diagnostic_tool

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.post("/execute", response_model=DiagnosticToolExecutionResponse)
async def run_diagnostic_tool(req: DiagnosticToolExecutionRequest):
    """Execute a deterministic, read-only diagnostic tool.
    
    If case_id is supplied, automatically records the diagnostic output to the case evidence timeline.
    """
    result = execute_diagnostic_tool(req.tool_name, req.params)

    # If linked to a case, record to evidence timeline
    if req.case_id and store.get_case(req.case_id):
        evidence_content = (
            f"Executed diagnostic tool '{req.tool_name}' ({result.execution_time_ms}ms):\n\n"
            f"Summary: {result.summary}\n\n"
            f"Raw Data:\n{json.dumps(result.data, indent=2)}"
        )
        ev_record = store.add_case_evidence(
            case_id=req.case_id,
            req=AddEvidenceRequest(
                source=EvidenceSource.SYSTEM,
                event_type=EvidenceType.DIAGNOSTIC_RUN,
                title=f"Diagnostic Tool: {req.tool_name}",
                content=evidence_content,
                metadata={
                    "tool_name": req.tool_name,
                    "params": req.params,
                    "execution_time_ms": result.execution_time_ms,
                    "success": result.success,
                },
            ),
            author="Diagnostic Workbench",
        )
        result.evidence_record_id = ev_record.id

    return result

