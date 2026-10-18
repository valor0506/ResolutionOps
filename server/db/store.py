import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from server.models.schemas import (
    Customer,
    Case,
    CaseStatus,
    CasePriority,
    CaseSeverity,
    EvidenceRecord,
    DiagnosticHypothesis,
    HypothesisStatus,
    KnowledgeArticle,
    EngineeringHandoff,
    HandoffStatus,
    VerificationResult,
    VerificationCriterion,
    AuditRecord,
    CaseCreateRequest,
    CaseUpdateRequest,
    AddEvidenceRequest,
)
from server.seed.data import (
    CUSTOMERS,
    CASES,
    CASE_EVIDENCE,
    CASE_HYPOTHESES,
    CASE_HANDOFFS,
    CASE_VERIFICATION,
    KNOWLEDGE_ARTICLES,
)


class DataStore:
    """Thread-safe application data store with pre-seeded realistic synthetic context."""

    def __init__(self):
        self._lock = threading.RLock()
        self.customers: Dict[str, Customer] = {c.id: c.model_copy(deep=True) for c in CUSTOMERS}
        self.cases: Dict[str, Case] = {c.id: c.model_copy(deep=True) for c in CASES}
        self.evidence: Dict[str, List[EvidenceRecord]] = {
            case_id: [ev.model_copy(deep=True) for ev in ev_list]
            for case_id, ev_list in CASE_EVIDENCE.items()
        }
        self.hypotheses: Dict[str, List[DiagnosticHypothesis]] = {
            case_id: [h.model_copy(deep=True) for h in hyp_list]
            for case_id, hyp_list in CASE_HYPOTHESES.items()
        }
        self.handoffs: Dict[str, EngineeringHandoff] = {
            case_id: h.model_copy(deep=True) for case_id, h in CASE_HANDOFFS.items()
        }
        self.verifications: Dict[str, VerificationResult] = {
            case_id: v.model_copy(deep=True) for case_id, v in CASE_VERIFICATION.items()
        }
        self.knowledge_articles: Dict[str, KnowledgeArticle] = {
            kb.id: kb.model_copy(deep=True) for kb in KNOWLEDGE_ARTICLES
        }
        self.audit_records: Dict[str, List[AuditRecord]] = {}

    # ========================================================================
    # Customers
    # ========================================================================

    def list_customers(self) -> List[Customer]:
        with self._lock:
            return list(self.customers.values())

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        with self._lock:
            return self.customers.get(customer_id)

    # ========================================================================
    # Cases
    # ========================================================================

    def list_cases(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        customer_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Case], int]:
        with self._lock:
            filtered = list(self.cases.values())

            if search:
                s = search.lower()
                filtered = [
                    c
                    for c in filtered
                    if s in c.title.lower()
                    or s in c.id.lower()
                    or s in c.customer_name.lower()
                    or s in c.summary.lower()
                ]

            if status:
                filtered = [c for c in filtered if c.status.value == status]

            if priority:
                filtered = [c for c in filtered if c.priority.value == priority]

            if customer_id:
                filtered = [c for c in filtered if c.customer_id == customer_id]

            # Sort: newest first
            filtered.sort(key=lambda c: c.created_at, reverse=True)

            total = len(filtered)
            start = (page - 1) * page_size
            end = start + page_size
            return filtered[start:end], total

    def get_case(self, case_id: str) -> Optional[Case]:
        with self._lock:
            return self.cases.get(case_id)

    def create_case(self, req: CaseCreateRequest, created_by: str = "Support Engineer") -> Case:
        with self._lock:
            customer = self.customers.get(req.customer_id)
            customer_name = customer.name if customer else "Unknown Customer"

            case_number = len(self.cases) + 892
            case_id = f"CASE-2026-{case_number:04d}"
            now = datetime.now(timezone.utc)

            new_case = Case(
                id=case_id,
                title=req.title,
                customer_id=req.customer_id,
                customer_name=customer_name,
                priority=req.priority,
                severity=req.severity,
                status=CaseStatus.NEW,
                assigned_owner_id=None,
                assigned_owner_name=None,
                related_incident_id=None,
                current_blocker=None,
                next_action="Review initial intake and collect missing diagnostics",
                summary=req.summary,
                symptoms=req.symptoms,
                expected_behavior=req.expected_behavior,
                actual_behavior=req.actual_behavior,
                reproduction_steps=req.reproduction_steps,
                environment=req.environment,
                app_version=req.app_version,
                timestamps=req.timestamps,
                request_ids=req.request_ids,
                error_messages=req.error_messages,
                missing_information=req.missing_information,
                created_at=now,
                updated_at=now,
            )

            self.cases[case_id] = new_case
            self.evidence[case_id] = []
            self.hypotheses[case_id] = []
            self.audit_records[case_id] = [
                AuditRecord(
                    id=f"audit-{uuid.uuid4().hex[:8]}",
                    case_id=case_id,
                    action="CASE_CREATED",
                    performed_by=created_by,
                    new_state=new_case.model_dump(mode="json"),
                    timestamp=now,
                )
            ]

            return new_case

    def update_case(
        self, case_id: str, req: CaseUpdateRequest, updated_by: str = "Support Engineer"
    ) -> Optional[Case]:
        with self._lock:
            case = self.cases.get(case_id)
            if not case:
                return None

            prev_state = case.model_dump(mode="json")
            update_data = req.model_dump(exclude_unset=True)

            # Verification gate: Case cannot be resolved unless verified
            if "status" in update_data and update_data["status"] == CaseStatus.RESOLVED:
                verification = self.verifications.get(case_id)
                if not verification or (not verification.all_passed and not verification.exception_documented):
                    raise ValueError(
                        "Cannot transition case to Resolved: required verification checklist has not passed "
                        "and no documented exception is recorded."
                    )

            for key, val in update_data.items():
                if val is not None:
                    setattr(case, key, val)

            case.updated_at = datetime.now(timezone.utc)
            self.cases[case_id] = case

            # Record audit event
            self._record_audit(
                case_id=case_id,
                action="CASE_UPDATED",
                performed_by=updated_by,
                previous_state=prev_state,
                new_state=case.model_dump(mode="json"),
            )

            return case

    # ========================================================================
    # Evidence Timeline
    # ========================================================================

    def get_case_evidence(self, case_id: str) -> List[EvidenceRecord]:
        with self._lock:
            ev_list = self.evidence.get(case_id, [])
            return sorted(ev_list, key=lambda e: e.timestamp)

    def add_case_evidence(
        self, case_id: str, req: AddEvidenceRequest, author: str = "Support Engineer"
    ) -> EvidenceRecord:
        with self._lock:
            if case_id not in self.cases:
                raise KeyError(f"Case '{case_id}' not found")

            ev_id = f"ev-{uuid.uuid4().hex[:8]}"
            now = datetime.now(timezone.utc)

            record = EvidenceRecord(
                id=ev_id,
                case_id=case_id,
                source=req.source,
                event_type=req.event_type,
                timestamp=now,
                title=req.title,
                content=req.content,
                metadata=req.metadata,
            )

            if case_id not in self.evidence:
                self.evidence[case_id] = []
            self.evidence[case_id].append(record)

            self._record_audit(
                case_id=case_id,
                action="EVIDENCE_ADDED",
                performed_by=author,
                new_state={"evidence_id": ev_id, "title": req.title, "event_type": req.event_type.value},
            )

            return record

    # ========================================================================
    # Hypotheses
    # ========================================================================

    def get_case_hypotheses(self, case_id: str) -> List[DiagnosticHypothesis]:
        with self._lock:
            return sorted(self.hypotheses.get(case_id, []), key=lambda h: h.rank)

    def set_case_hypotheses(
        self, case_id: str, hypotheses: List[DiagnosticHypothesis], author: str = "AI Assistant"
    ):
        with self._lock:
            self.hypotheses[case_id] = hypotheses
            self._record_audit(
                case_id=case_id,
                action="HYPOTHESES_GENERATED",
                performed_by=author,
                new_state={"count": len(hypotheses)},
            )

    def update_hypothesis_status(
        self, case_id: str, hypothesis_id: str, new_status: HypothesisStatus, updated_by: str = "Support Engineer"
    ) -> Optional[DiagnosticHypothesis]:
        with self._lock:
            hyp_list = self.hypotheses.get(case_id, [])
            for h in hyp_list:
                if h.id == hypothesis_id:
                    h.status = new_status
                    self._record_audit(
                        case_id=case_id,
                        action="HYPOTHESIS_STATUS_CHANGED",
                        performed_by=updated_by,
                        new_state={"hypothesis_id": hypothesis_id, "status": new_status.value},
                    )
                    return h
            return None

    # ========================================================================
    # Engineering Handoff
    # ========================================================================

    def get_case_handoff(self, case_id: str) -> Optional[EngineeringHandoff]:
        with self._lock:
            return self.handoffs.get(case_id)

    def save_case_handoff(
        self, case_id: str, handoff: EngineeringHandoff, updated_by: str = "Support Engineer"
    ) -> EngineeringHandoff:
        with self._lock:
            self.handoffs[case_id] = handoff
            self._record_audit(
                case_id=case_id,
                action="HANDOFF_UPDATED",
                performed_by=updated_by,
                new_state={"handoff_id": handoff.id, "status": handoff.status.value, "is_complete": handoff.is_complete},
            )
            return handoff

    # ========================================================================
    # Verification Checklist
    # ========================================================================

    def get_case_verification(self, case_id: str) -> Optional[VerificationResult]:
        with self._lock:
            return self.verifications.get(case_id)

    def update_case_verification(
        self, case_id: str, verification: VerificationResult, updated_by: str = "Authorized Approver"
    ) -> VerificationResult:
        with self._lock:
            self.verifications[case_id] = verification
            self._record_audit(
                case_id=case_id,
                action="VERIFICATION_UPDATED",
                performed_by=updated_by,
                new_state={"all_passed": verification.all_passed, "approved_by": verification.approved_by},
            )
            return verification

    # ========================================================================
    # Knowledge Base
    # ========================================================================

    def list_knowledge_articles(
        self, query: Optional[str] = None, product_area: Optional[str] = None, tag: Optional[str] = None
    ) -> List[KnowledgeArticle]:
        with self._lock:
            articles = list(self.knowledge_articles.values())

            if query:
                q = query.lower()
                articles = [
                    a
                    for a in articles
                    if q in a.title.lower()
                    or q in a.description.lower()
                    or any(q in s.lower() for s in a.symptoms)
                    or any(q in c.lower() for c in a.known_causes)
                    or any(q in t.lower() for t in a.tags)
                ]

            if product_area:
                articles = [a for a in articles if a.product_area == product_area]

            if tag:
                articles = [a for a in articles if tag in a.tags]

            return articles

    def get_knowledge_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        with self._lock:
            return self.knowledge_articles.get(article_id)

    # ========================================================================
    # Overview Metrics & Calculations
    # ========================================================================

    def get_overview_metrics(self) -> Dict[str, Any]:
        with self._lock:
            all_cases = list(self.cases.values())
            total_cases = len(all_cases)

            open_cases = [c for c in all_cases if c.status not in (CaseStatus.RESOLVED, CaseStatus.CLOSED)]
            awaiting_customer = [c for c in all_cases if c.status == CaseStatus.AWAITING_CUSTOMER]
            awaiting_engineering = [c for c in all_cases if c.status == CaseStatus.AWAITING_ENGINEERING]
            resolved_verified = [c for c in all_cases if c.status == CaseStatus.RESOLVED]
            high_priority = [c for c in all_cases if c.priority in (CasePriority.HIGH, CasePriority.CRITICAL)]
            unowned = [c for c in all_cases if not c.assigned_owner_id]

            # Status distribution
            status_distribution = {}
            for status in CaseStatus:
                status_distribution[status.value] = sum(1 for c in all_cases if c.status == status)

            # Priority distribution
            priority_distribution = {}
            for prio in CasePriority:
                priority_distribution[prio.value] = sum(1 for c in all_cases if c.priority == prio)

            # Recent activity timeline
            recent_activity = []
            for case in sorted(all_cases, key=lambda c: c.updated_at, reverse=True)[:5]:
                recent_activity.append(
                    {
                        "case_id": case.id,
                        "title": case.title,
                        "customer_name": case.customer_name,
                        "status": case.status.value,
                        "priority": case.priority.value,
                        "updated_at": case.updated_at.isoformat(),
                    }
                )

            return {
                "total_open_cases": len(open_cases),
                "total_cases": total_cases,
                "cases_awaiting_customer": len(awaiting_customer),
                "cases_awaiting_engineering": len(awaiting_engineering),
                "cases_resolved_and_verified": len(resolved_verified),
                "high_priority_incidents": len(high_priority),
                "unowned_cases": len(unowned),
                "average_time_to_resolution_hours": 3.8,  # Synthetic measured SLA metric
                "status_distribution": status_distribution,
                "priority_distribution": priority_distribution,
                "recent_activity": recent_activity,
                "is_demonstration_data": True,
            }

    # ========================================================================
    # Audit Trail Helper
    # ========================================================================

    def _record_audit(
        self,
        case_id: str,
        action: str,
        performed_by: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
    ):
        if case_id not in self.audit_records:
            self.audit_records[case_id] = []

        rec = AuditRecord(
            id=f"audit-{uuid.uuid4().hex[:8]}",
            case_id=case_id,
            action=action,
            performed_by=performed_by,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
        )
        self.audit_records[case_id].append(rec)

    def get_case_audit_trail(self, case_id: str) -> List[AuditRecord]:
        with self._lock:
            return sorted(self.audit_records.get(case_id, []), key=lambda a: a.timestamp, reverse=True)


# Global singleton instance
store = DataStore()
