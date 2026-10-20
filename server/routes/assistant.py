from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from server.ai.assistant import ask_assistant

router = APIRouter(prefix="/assistant", tags=["assistant"])


class AssistantMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class AskRequest(BaseModel):
    question: str
    conversation_history: Optional[List[AssistantMessage]] = None


class AskResponse(BaseModel):
    answer: str
    case_id: str


@router.post("/cases/{case_id}/ask", response_model=AskResponse)
async def ask_case_question(case_id: str, req: AskRequest):
    """Ask a natural language question about a specific case, grounded in its evidence."""
    if not req.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="question must not be empty",
        )

    history = None
    if req.conversation_history:
        history = [{"role": m.role, "content": m.content} for m in req.conversation_history]

    answer = await ask_assistant(case_id, req.question.strip(), history)
    return AskResponse(answer=answer, case_id=case_id)

