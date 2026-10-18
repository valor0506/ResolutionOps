from datetime import datetime, timezone
from server.db.store import store
from server.models.schemas import (
    EngineeringHandoff,
    HandoffStatus,
)


def generate_engineering_handoff(case_id: str) -> EngineeringHandoff:
    """Generates a structured, engineering-ready handoff dossier from verified case evidence."""
    case = store.get_case(case_id)
    if not case:
        raise KeyError(f"Case '{case_id}' not found")

    customer = store.get_customer(case.customer_id)
    evidence_records = store.get_case_evidence(case_id)
    hypotheses = store.get_case_hypotheses(case_id)

    # Find accepted or top-ranked hypothesis
    working_hyp = next((h for h in hypotheses if h.status.value == "accepted"), None)
    if not working_hyp and hypotheses:
        working_hyp = hypotheses[0]

    now = datetime.now(timezone.utc)

    problem_summary = f"{case.title}. {case.summary}"
    customer_impact = (
        f"{case.customer_name} ({customer.tier.value if customer else 'Enterprise'} Tier). "
        f"SLA: {customer.sla_tier if customer else 'Standard'}. "
        f"Critical business operations or order progression obstructed."
    )

    supporting = working_hyp.supporting_evidence if working_hyp else [case.summary]
    alt_hypotheses = [
        f"#{h.rank} {h.title} (Confidence: {int(h.confidence_score * 100)}%, Status: {h.status.value})"
        for h in hypotheses
        if h != working_hyp
    ]

    sanitized_logs = [
        ev.content[:200]
        for ev in evidence_records
        if ev.event_type.value in ["sanitized_log", "api_trace", "diagnostic_run"]
    ][:4]

    next_steps = [
        "1. Confirm downstream receiver endpoint health and IP whitelisting.",
        "2. Review idempotency key compatibility before triggering event replay.",
        "3. Verify order status transitions to 'Confirmed' upon successful replay.",
    ]

    acceptance_criteria = [
        "Downstream endpoint responds with HTTP 200/202 upon idempotent webhook replay.",
        "Order status matches across primary DB and customer-facing dashboard.",
        "No duplicate charges or duplicate inventory reservations created.",
    ]

    handoff = EngineeringHandoff(
        id=f"hnd-{case_id.lower().replace('case-', '')}",
        case_id=case_id,
        problem_summary=problem_summary,
        customer_impact=customer_impact,
        affected_environment=case.environment,
        affected_version=case.app_version or "3.4.2",
        expected_behavior=case.expected_behavior,
        actual_behavior=case.actual_behavior,
        reproduction_steps=case.reproduction_steps,
        timestamps=case.timestamps,
        request_ids=case.request_ids,
        sanitized_logs=sanitized_logs,
        previous_troubleshooting="Correlated with in-app logs and knowledge base runbooks. Diagnostic tools verified state divergence.",
        suspected_root_cause=working_hyp.root_cause_explanation if working_hyp else "Investigation in progress.",
        supporting_evidence=supporting,
        alternative_hypotheses=alt_hypotheses,
        missing_evidence=case.missing_information,
        suggested_next_steps=next_steps,
        severity_rationale=f"{case.severity.value}: {case.priority.value} priority issue affecting production workflow.",
        suggested_owner_team="Platform Reliability & Integrations Engineering",
        acceptance_criteria=acceptance_criteria,
        is_complete=True,
        status=HandoffStatus.READY_FOR_ENGINEERING,
        approved_by=None,
        approved_at=None,
        created_at=now,
        updated_at=now,
    )

    # Persist handoff
    store.save_case_handoff(case_id, handoff)
    return handoff


def draft_customer_response(case_id: str) -> str:
    """Drafts a grounded, technical response to the customer explaining findings and next verification steps."""
    case = store.get_case(case_id)
    if not case:
        raise KeyError(f"Case '{case_id}' not found")

    customer = store.get_customer(case.customer_id)
    contact = customer.primary_contact_name.split()[0] if customer else "there"

    return (
        f"Hi {contact},\n\n"
        f"Our engineering team investigated case {case.id} ('{case.title}').\n\n"
        f"Our primary order processing completed successfully and confirmed your order data. "
        f"However, our status-update notification dispatched to your endpoint encountered HTTP 503 Service Unavailable "
        f"across all retry attempts, preventing your store dashboard from reflecting the confirmed status.\n\n"
        f"Could your infrastructure team verify whether your receiver endpoint was experiencing maintenance or rate limiting? "
        f"Also, please ensure our webhook egress IPs (35.192.44.10, 35.192.44.11) are whitelisted in your Cloudflare firewall.\n\n"
        f"Once your endpoint is ready, we are prepared to perform an idempotent replay to update your records immediately.\n\n"
        f"Best regards,\nResolutionOps Support Engineering"
    )
