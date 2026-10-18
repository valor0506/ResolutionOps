from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class CustomerTier(str, Enum):
    STARTER = "Starter"
    GROWTH = "Growth"
    ENTERPRISE = "Enterprise"


class CaseStatus(str, Enum):
    NEW = "New"
    INVESTIGATING = "Investigating"
    AWAITING_CUSTOMER = "Awaiting Customer"
    AWAITING_ENGINEERING = "Awaiting Engineering"
    FIX_IN_PROGRESS = "Fix In Progress"
    PENDING_VERIFICATION = "Pending Verification"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class CasePriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class CaseSeverity(str, Enum):
    SEV1 = "Sev-1"
    SEV2 = "Sev-2"
    SEV3 = "Sev-3"
    SEV4 = "Sev-4"


class EvidenceSource(str, Enum):
    CUSTOMER = "customer"
    SYSTEM = "system"
    AI_HYPOTHESIS = "ai_hypothesis"
    ENGINEER = "engineer"


class EvidenceType(str, Enum):
    CUSTOMER_MESSAGE = "customer_message"
    INTERNAL_NOTE = "internal_note"
    SANITIZED_LOG = "sanitized_log"
    API_TRACE = "api_trace"
    KB_REFERENCE = "kb_reference"
    DIAGNOSTIC_RUN = "diagnostic_run"
    VERIFICATION_RESULT = "verification_result"


class HypothesisStatus(str, Enum):
    PROPOSED = "proposed"
    INVESTIGATING = "investigating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class HandoffStatus(str, Enum):
    DRAFT = "draft"
    READY_FOR_ENGINEERING = "ready_for_engineering"
    ACCEPTED = "accepted"


# ============================================================================
# Core Domain Models
# ============================================================================

class Customer(BaseModel):
    id: str
    name: str
    domain: str
    tier: CustomerTier
    sla_tier: str = "99.9%"
    environment: str = "production"
    app_version: str = "3.4.2"
    primary_contact_name: str
    primary_contact_email: str
    created_at: datetime
    updated_at: datetime
    active_blockers: List[str] = Field(default_factory=list)
    known_commitments: List[str] = Field(default_factory=list)


class EvidenceRecord(BaseModel):
    id: str
    case_id: str
    source: EvidenceSource
    event_type: EvidenceType
    timestamp: datetime
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DiagnosticHypothesis(BaseModel):
    id: str
    case_id: str
    rank: int
    title: str
    root_cause_explanation: str
    supporting_evidence: List[str] = Field(default_factory=list)
    contradictory_evidence: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str
    recommended_test: str
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    generated_at: datetime


class KnowledgeArticle(BaseModel):
    id: str
    title: str
    product_area: str
    description: str
    symptoms: List[str] = Field(default_factory=list)
    known_causes: List[str] = Field(default_factory=list)
    diagnostic_steps: List[str] = Field(default_factory=list)
    resolution_steps: List[str] = Field(default_factory=list)
    applicable_versions: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    source: str
    updated_at: datetime


class EngineeringHandoff(BaseModel):
    id: str
    case_id: str
    problem_summary: str
    customer_impact: str
    affected_environment: str
    affected_version: str
    expected_behavior: str
    actual_behavior: str
    reproduction_steps: List[str] = Field(default_factory=list)
    timestamps: List[str] = Field(default_factory=list)
    request_ids: List[str] = Field(default_factory=list)
    sanitized_logs: List[str] = Field(default_factory=list)
    previous_troubleshooting: str
    suspected_root_cause: str
    supporting_evidence: List[str] = Field(default_factory=list)
    alternative_hypotheses: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    suggested_next_steps: List[str] = Field(default_factory=list)
    severity_rationale: str
    suggested_owner_team: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    is_complete: bool = False
    status: HandoffStatus = HandoffStatus.DRAFT
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class VerificationCriterion(BaseModel):
    id: str
    description: str
    passed: bool = False
    evidence: Optional[str] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None


class VerificationResult(BaseModel):
    id: str
    case_id: str
    criteria: List[VerificationCriterion] = Field(default_factory=list)
    all_passed: bool = False
    approved_by: Optional[str] = None
    exception_documented: Optional[str] = None
    verified_at: Optional[datetime] = None


class Case(BaseModel):
    id: str
    title: str
    customer_id: str
    customer_name: str
    priority: CasePriority
    severity: CaseSeverity
    status: CaseStatus
    assigned_owner_id: Optional[str] = None
    assigned_owner_name: Optional[str] = None
    related_incident_id: Optional[str] = None
    current_blocker: Optional[str] = None
    next_action: Optional[str] = None

    # Structured issue report details
    summary: str
    symptoms: List[str] = Field(default_factory=list)
    expected_behavior: str
    actual_behavior: str
    reproduction_steps: List[str] = Field(default_factory=list)
    environment: str = "production"
    app_version: Optional[str] = None
    timestamps: List[str] = Field(default_factory=list)
    request_ids: List[str] = Field(default_factory=list)
    error_messages: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)

    # Resolution attributes
    current_diagnosis: Optional[str] = None
    recommended_action: Optional[str] = None
    resolution_notes: Optional[str] = None
    customer_response_draft: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class AuditRecord(BaseModel):
    id: str
    case_id: str
    action: str
    performed_by: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    timestamp: datetime


# ============================================================================
# API Request / Response Payloads
# ============================================================================

class CaseCreateRequest(BaseModel):
    title: str
    customer_id: str
    priority: CasePriority = CasePriority.MEDIUM
    severity: CaseSeverity = CaseSeverity.SEV3
    summary: str
    expected_behavior: str
    actual_behavior: str
    symptoms: List[str] = Field(default_factory=list)
    reproduction_steps: List[str] = Field(default_factory=list)
    environment: str = "production"
    app_version: Optional[str] = None
    timestamps: List[str] = Field(default_factory=list)
    request_ids: List[str] = Field(default_factory=list)
    error_messages: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class CaseUpdateRequest(BaseModel):
    title: Optional[str] = None
    priority: Optional[CasePriority] = None
    severity: Optional[CaseSeverity] = None
    status: Optional[CaseStatus] = None
    assigned_owner_id: Optional[str] = None
    assigned_owner_name: Optional[str] = None
    current_blocker: Optional[str] = None
    next_action: Optional[str] = None
    current_diagnosis: Optional[str] = None
    recommended_action: Optional[str] = None
    resolution_notes: Optional[str] = None
    customer_response_draft: Optional[str] = None


class AddEvidenceRequest(BaseModel):
    source: EvidenceSource
    event_type: EvidenceType
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntakeParseRequest(BaseModel):
    unstructured_complaint: str
    customer_id: Optional[str] = None


class IntakeParseResponse(BaseModel):
    concise_summary: str
    suggested_customer_id: Optional[str] = None
    suggested_customer_name: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    known_reproduction_steps: List[str] = Field(default_factory=list)
    environment: Optional[str] = None
    available_timestamps: List[str] = Field(default_factory=list)
    request_ids: List[str] = Field(default_factory=list)
    error_evidence: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    clarification_questions: List[str] = Field(default_factory=list)
    suggested_severity: CaseSeverity
    severity_rationale: str
    uncertainties: List[str] = Field(default_factory=list)


class DiagnosticToolExecutionRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    case_id: Optional[str] = None


class DiagnosticToolExecutionResponse(BaseModel):
    tool_name: str
    execution_time_ms: int
    success: bool
    summary: str
    data: Any
    evidence_record_id: Optional[str] = None
