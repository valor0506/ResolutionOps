import json
import re
from typing import Optional
from server.ai.client import gemini_manager
from server.ai.prompts import INTAKE_SYSTEM_PROMPT
from server.db.store import store
from server.models.schemas import (
    IntakeParseResponse,
    CaseSeverity,
)


def _deterministic_intake_fallback(
    complaint: str, customer_id: Optional[str] = None
) -> IntakeParseResponse:
    """High-fidelity deterministic intake extractor used when Gemini is unconfigured or unavailable."""
    text_lower = complaint.lower()

    # Match customer if not provided
    cust_name = None
    if customer_id:
        cust = store.get_customer(customer_id)
        if cust:
            cust_name = cust.name
    else:
        for c in store.list_customers():
            if c.name.lower() in text_lower or c.domain.lower() in text_lower:
                customer_id = c.id
                cust_name = c.name
                break

    # Extract IDs via regex (ORD-*, req-*, trace-*, UUIDs)
    found_order_ids = re.findall(r"(?:ORD-[\w-]+|#\d+)", complaint, re.IGNORECASE)
    found_request_ids = re.findall(r"(?:req-[\w-]+|trace-[\w-]+)", complaint, re.IGNORECASE)

    # Extract error codes
    error_evidence = []
    if "503" in complaint:
        error_evidence.append("HTTP 503 Service Unavailable mentioned in report")
    if "504" in complaint or "timeout" in text_lower:
        error_evidence.append("Gateway timeout / request deadline exceeded")
    if "429" in complaint or "rate limit" in text_lower:
        error_evidence.append("HTTP 429 Rate Limiting detected")
    if "401" in complaint or "unauthorized" in text_lower:
        error_evidence.append("HTTP 401 Authentication failure")

    # Determine severity
    if any(k in text_lower for k in ["critical", "outage", "stuck", "pending", "blocked", "all orders", "failing"]):
        suggested_sev = CaseSeverity.SEV1 if any(k in text_lower for k in ["fulfillment", "payment", "all orders", "enterprise"]) else CaseSeverity.SEV2
        sev_rationale = "Customer core operations or order processing is blocked. Direct impact on business workflow."
    elif any(k in text_lower for k in ["slow", "intermittent", "batch", "rate limit"]):
        suggested_sev = CaseSeverity.SEV2
        sev_rationale = "Significant disruption affecting batch processing or throughput, but not complete system outage."
    elif any(k in text_lower for k in ["csv", "export", "typo", "display", "accent", "weird"]):
        suggested_sev = CaseSeverity.SEV4
        sev_rationale = "Cosmetic, minor display anomaly or client-side inconvenience with low business impact."
    else:
        suggested_sev = CaseSeverity.SEV3
        sev_rationale = "Moderate defect without catastrophic workflow stoppage."

    # Identify missing fields
    missing_info = []
    clarification_qs = []

    if not found_request_ids:
        missing_info.append("Request correlation ID or API gateway trace ID (e.g. X-Correlation-ID)")
        clarification_qs.append("Could you provide the exact correlation or request ID returned in the API response headers?")

    if not any(k in text_lower for k in ["utc", "am", "pm", ":", "2026", "yesterday", "today", "at "]):
        missing_info.append("Precise UTC timestamp of failure")
        clarification_qs.append("What was the exact timestamp (and timezone) when the error occurred?")

    if not any(k in text_lower for k in ["prod", "staging", "cluster", "version"]):
        missing_info.append("Environment and deployment version details")
        clarification_qs.append("Did this occur in your Production or Staging/Sandbox environment?")

    if not any(k in text_lower for k in ["step", "first", "then", "reproduce", "curl", "post", "payload"]):
        missing_info.append("Step-by-step reproduction instructions")
        clarification_qs.append("What specific API call, endpoint, or dashboard action triggered this behavior?")

    # Formulate concise summary
    first_sentence = complaint.strip().split(".")[0]
    concise_summary = first_sentence if len(first_sentence) < 120 else first_sentence[:117] + "..."

    return IntakeParseResponse(
        concise_summary=concise_summary,
        suggested_customer_id=customer_id or "cust-northstar",
        suggested_customer_name=cust_name or "Northstar Commerce",
        expected_behavior="Target workflow or API call completes successfully and downstream status updates accordingly.",
        actual_behavior=complaint.strip(),
        known_reproduction_steps=[
            f"1. Trigger reported workflow: '{concise_summary}'",
            "2. Inspect system state and observe discrepancies reported by customer.",
        ],
        environment="production",
        available_timestamps=["Extracted from intake submission time"],
        request_ids=found_order_ids + found_request_ids,
        error_evidence=error_evidence,
        missing_information=missing_info,
        clarification_questions=clarification_qs,
        suggested_severity=suggested_sev,
        severity_rationale=sev_rationale,
        uncertainties=[
            "Whether the failure was intermittent or consistent.",
            "Customer-side network, WAF, or proxy configuration status.",
        ],
    )


async def parse_unstructured_intake(
    complaint: str, customer_id: Optional[str] = None
) -> IntakeParseResponse:
    """Converts raw unstructured customer complaints into structured issue reports using Gemini with deterministic fallback."""
    client = gemini_manager.get_client()

    if not client:
        return _deterministic_intake_fallback(complaint, customer_id)

    # If Gemini is configured, invoke model with structured output schema
    prompt = f"""Customer Complaint:
\"\"\"{complaint}\"\"\"

Pre-selected Customer ID: {customer_id or 'None'}

Convert this into a structured IntakeParseResponse. Adhere strictly to the system rules."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "system_instruction": INTAKE_SYSTEM_PROMPT,
                "response_mime_type": "application/json",
                "response_schema": IntakeParseResponse,
                "temperature": 0.1,  # Low temperature for strict factual extraction
            },
        )
        if response.text:
            parsed_data = json.loads(response.text)
            return IntakeParseResponse.model_validate(parsed_data)
        else:
            return _deterministic_intake_fallback(complaint, customer_id)
    except Exception as e:
        # Graceful fallback on quota, timeout, or formatting error
        return _deterministic_intake_fallback(complaint, customer_id)
