"""
Conversational Investigation Assistant — natural language Q&A grounded in case evidence.

The assistant answers questions about a specific case by searching the evidence timeline,
diagnostic hypotheses, knowledge base articles, and customer context.  It never fabricates
information; every claim cites an evidence ID or knowledge article ID.
"""

import json
from typing import List
from server.ai.client import gemini_manager
from server.ai.investigator import _build_context_package
from server.db.store import store


ASSISTANT_SYSTEM_PROMPT = """You are ResolutionOps Investigation Assistant — a grounded, evidence-citing Q&A agent.

CONTEXT:
You are given a structured case investigation package containing:
- Case metadata (ID, title, severity, status, summary)
- Customer context (tier, SLA, environment, version, known blockers)
- Evidence timeline (timestamped events with unique IDs like ev-001, ev-002)
- Correlated knowledge articles (KB-001, KB-002, etc.)
- Diagnostic hypotheses (if any exist)

RULES:
1. ONLY use information present in the provided context package. NEVER invent facts.
2. When citing evidence, always include the evidence ID (e.g., "According to ev-004, the webhook...").
3. When citing knowledge articles, include the article ID (e.g., "KB-002 recommends...").
4. If the user asks something that cannot be answered from the available evidence, say explicitly:
   "I don't have enough evidence in this case to answer that. You may want to run [specific diagnostic tool]."
5. Keep answers concise, technical, and directly actionable.
6. Format answers in plain text paragraphs — do not use markdown headers or bullet lists unless listing evidence IDs.
7. Never suggest closing or resolving the case. Only describe findings and recommend next diagnostic steps.
"""


def _deterministic_answer(question: str, case_id: str) -> str:
    """Produces a grounded answer using keyword matching against case evidence."""
    case = store.get_case(case_id)
    if not case:
        return f"Case '{case_id}' was not found in the system."

    evidence = store.get_case_evidence(case_id)
    hypotheses = store.get_case_hypotheses(case_id)
    q = question.lower()

    # Common question patterns with grounded answers
    if any(kw in q for kw in ["what happened", "summary", "what is this", "describe", "overview"]):
        return (
            f"Case {case.id} — \"{case.title}\" — was reported by {case.customer_name}. "
            f"Summary: {case.summary} "
            f"Expected behavior: {case.expected_behavior}. "
            f"Actual behavior: {case.actual_behavior}. "
            f"There are currently {len(evidence)} evidence records and {len(hypotheses)} diagnostic hypotheses on file."
        )

    if any(kw in q for kw in ["root cause", "hypothesis", "why", "cause", "diagnosis"]):
        if hypotheses:
            top = hypotheses[0]
            return (
                f"The highest-ranked hypothesis (confidence {top.confidence_score:.0%}) is: "
                f"\"{top.title}\". "
                f"Explanation: {top.root_cause_explanation} "
                f"Supporting evidence: {', '.join(top.supporting_evidence)}."
            )
        return "No hypotheses have been generated yet. Run 'AI Re-Investigate' from the Hypotheses tab to generate ranked root-cause hypotheses."

    if any(kw in q for kw in ["evidence", "timeline", "log", "trace"]):
        if not evidence:
            return "No evidence records have been collected for this case yet."
        summary_lines = [f"- {ev.id}: [{ev.source.value}/{ev.event_type.value}] {ev.title}" for ev in evidence[:8]]
        return f"The case has {len(evidence)} evidence records. Here are the key entries:\n" + "\n".join(summary_lines)

    if any(kw in q for kw in ["customer", "who reported", "contact", "tier", "sla"]):
        customer = store.get_customer(case.customer_id)
        if customer:
            return (
                f"Customer: {customer.name} (ID: {customer.id}). "
                f"Tier: {customer.tier.value}, SLA: {customer.sla_tier}. "
                f"Environment: {customer.environment}, App Version: v{customer.app_version}. "
                f"Technical Contact: {customer.primary_contact_name} ({customer.primary_contact_email}). "
                + (f"Active Blocker: {customer.active_blockers[0]}" if customer.active_blockers else "No active blockers.")
            )
        return f"Customer ID '{case.customer_id}' — {case.customer_name}."

    if any(kw in q for kw in ["next step", "what should", "recommend", "action", "what do i do"]):
        if hypotheses:
            top = hypotheses[0]
            return (
                f"Based on the top hypothesis ({top.title}), the recommended next step is: {top.recommended_test}. "
                f"You can also generate an Engineering Handoff from the Handoff tab if escalation is needed."
            )
        return "Start by running diagnostic tools from the Diagnostic Workbench tab, then generate hypotheses with 'AI Re-Investigate'."

    if any(kw in q for kw in ["webhook", "503", "retry", "downstream"]):
        relevant = [ev for ev in evidence if "503" in ev.content or "webhook" in ev.title.lower()]
        if relevant:
            lines = [f"- {ev.id}: {ev.title} — {ev.content[:120]}" for ev in relevant[:4]]
            return f"Found {len(relevant)} evidence records related to webhook/503 failures:\n" + "\n".join(lines)
        return "No webhook or 503-related evidence found in this case's timeline."

    if any(kw in q for kw in ["handoff", "escalat", "engineering"]):
        handoff = store.get_case_handoff(case_id)
        if handoff:
            return (
                f"An engineering handoff exists for this case (status: {handoff.status.value}). "
                f"Suspected root cause: {handoff.suspected_root_cause}. "
                f"Target team: {handoff.suggested_owner_team}."
            )
        return "No engineering handoff has been generated yet. Use 'Regenerate with AI' on the Engineering Handoff tab."

    if any(kw in q for kw in ["verification", "resolved", "close", "gate"]):
        ver = store.get_case_verification(case_id)
        if ver:
            passed = sum(1 for c in ver.criteria if c.passed)
            total = len(ver.criteria)
            return (
                f"Verification gate: {passed}/{total} criteria passed. "
                f"{'All criteria met — case can be closed.' if ver.all_passed else 'Case CANNOT be resolved until all criteria pass or an exception is documented.'}"
            )
        return "No verification checklist has been created for this case."

    # Fallback: search evidence content for keyword matches
    keywords = [w for w in q.split() if len(w) > 3]
    matched = []
    for ev in evidence:
        if any(kw in ev.content.lower() or kw in ev.title.lower() for kw in keywords):
            matched.append(ev)

    if matched:
        lines = [f"- {ev.id}: {ev.title}" for ev in matched[:5]]
        return f"I found {len(matched)} evidence records mentioning your search terms:\n" + "\n".join(lines) + "\n\nCould you ask a more specific question about these findings?"

    return (
        "I don't have enough evidence in this case to answer that specifically. "
        "Try asking about the root cause, evidence timeline, customer context, or next recommended steps. "
        "You can also run diagnostic tools from the Diagnostic Workbench to collect more data."
    )


async def ask_assistant(case_id: str, question: str, conversation_history: List[dict] = None) -> str:
    """Answer a natural language question about a specific case, grounded in its evidence."""
    case = store.get_case(case_id)
    if not case:
        return f"Case '{case_id}' was not found in the system."

    client = gemini_manager.get_client()

    if not client:
        return _deterministic_answer(question, case_id)

    try:
        context_package = _build_context_package(case_id)

        # Include hypotheses in the context
        hypotheses = store.get_case_hypotheses(case_id)
        context_package["hypotheses"] = [
            {
                "id": h.id,
                "rank": h.rank,
                "title": h.title,
                "explanation": h.root_cause_explanation,
                "confidence": h.confidence_score,
                "status": h.status.value,
            }
            for h in hypotheses
        ]

        # Include handoff if exists
        handoff = store.get_case_handoff(case_id)
        if handoff:
            context_package["handoff"] = {
                "status": handoff.status.value,
                "suspected_root_cause": handoff.suspected_root_cause,
                "target_team": handoff.suggested_owner_team,
            }

        # Build conversation context
        messages = f"Case Investigation Context:\n{json.dumps(context_package, indent=2)}\n\n"
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages += f"{role.upper()}: {content}\n"

        messages += f"USER: {question}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config={
                "system_instruction": ASSISTANT_SYSTEM_PROMPT,
                "temperature": 0.3,
            },
        )

        if response.text:
            return response.text.strip()
        return _deterministic_answer(question, case_id)

    except Exception:
        return _deterministic_answer(question, case_id)

