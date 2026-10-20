import unittest
from fastapi.testclient import TestClient
from server.main import app
from server.models.schemas import CaseStatus


class TestResolutionOpsAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "service": "resolutionops-api"})

    def test_customers_list(self):
        res = self.client.get("/api/customers")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 5)
        northstar = next((c for c in data if c["id"] == "cust-northstar"), None)
        self.assertIsNotNone(northstar)
        self.assertEqual(northstar["tier"], "Enterprise")
        self.assertIn("99.99%", northstar["sla_tier"])

    def test_cases_listing_and_filtering(self):
        # 1. Total count
        res = self.client.get("/api/cases")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total"], 10)

        # 2. Search Northstar
        res = self.client.get("/api/cases?search=Northstar")
        self.assertEqual(res.status_code, 200)
        items = res.json()["items"]
        self.assertGreaterEqual(len(items), 2)

        # 3. Filter by priority
        res = self.client.get("/api/cases?priority=Critical")
        self.assertEqual(res.status_code, 200)
        for c in res.json()["items"]:
            self.assertEqual(c["priority"], "Critical")

    def test_flagship_northstar_incident(self):
        res = self.client.get("/api/cases/CASE-2026-0891")
        self.assertEqual(res.status_code, 200)
        c = res.json()
        self.assertEqual(c["customer_name"], "Northstar Commerce")
        self.assertEqual(c["status"], "Investigating")
        self.assertIn("ORD-98421", c["summary"])
        self.assertIn("req-8849-a1fc-9920", c["request_ids"])

        # Check evidence
        ev_res = self.client.get("/api/cases/CASE-2026-0891/evidence")
        self.assertEqual(ev_res.status_code, 200)
        evidence = ev_res.json()
        self.assertGreaterEqual(len(evidence), 6)
        # Verify 503 webhook log is present
        self.assertTrue(any("503" in ev["title"] or "503" in ev["content"] for ev in evidence))

        # Check hypotheses
        hyp_res = self.client.get("/api/cases/CASE-2026-0891/hypotheses")
        self.assertEqual(hyp_res.status_code, 200)
        hypotheses = hyp_res.json()
        self.assertEqual(len(hypotheses), 3)
        rank1 = hypotheses[0]
        self.assertIn("Webhook", rank1["title"])
        self.assertGreater(rank1["confidence_score"], 0.8)

    def test_diagnostic_tool_execution(self):
        # Run inspect_webhook_logs on Northstar
        res = self.client.post(
            "/api/diagnostics/execute",
            json={
                "tool_name": "inspect_webhook_logs",
                "params": {"customer_id": "cust-northstar", "order_id": "ORD-98421"},
                "case_id": "CASE-2026-0891",
            },
        )
        self.assertEqual(res.status_code, 200)
        result = res.json()
        self.assertTrue(result["success"])
        self.assertIn("503", result["summary"])
        self.assertIsNotNone(result.get("evidence_record_id"))

        # Verify new evidence was appended to the case timeline
        ev_res = self.client.get("/api/cases/CASE-2026-0891/evidence")
        self.assertTrue(any(ev["id"] == result["evidence_record_id"] for ev in ev_res.json()))

    def test_verification_gate_prevents_premature_resolution(self):
        # Attempt to mark CASE-2026-0891 as Resolved before criteria pass
        res = self.client.patch(
            "/api/cases/CASE-2026-0891",
            json={"status": CaseStatus.RESOLVED.value},
        )
        # Should return 422 Unprocessable Entity
        self.assertEqual(res.status_code, 422)
        self.assertIn("verification checklist has not passed", res.json()["detail"])

    def test_ai_intake_parse(self):
        complaint = (
            "Our API returned 200 for order ORD-98421 at 04:15 UTC, but dashboard says pending. "
            "Trace ID is req-8849-a1fc. This is blocking fulfillment for our enterprise buyers."
        )
        res = self.client.post(
            "/api/ai/intake-parse",
            json={"unstructured_complaint": complaint, "customer_id": "cust-northstar"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["concise_summary"]) > 0)
        self.assertIn("ORD-98421", data["request_ids"])
        self.assertEqual(data["suggested_severity"], "Sev-1")
        self.assertGreaterEqual(len(data["clarification_questions"]), 1)

    def test_ai_investigate_and_handoff(self):
        # 1. Investigate
        res = self.client.post("/api/ai/cases/CASE-2026-0891/investigate")
        self.assertEqual(res.status_code, 200)
        hypotheses = res.json()["hypotheses"]
        self.assertGreaterEqual(len(hypotheses), 1)

        # 2. Handoff
        hnd_res = self.client.post("/api/ai/cases/CASE-2026-0891/generate-handoff")
        self.assertEqual(hnd_res.status_code, 200)
        handoff = hnd_res.json()
        self.assertTrue(handoff["is_complete"])
        self.assertEqual(handoff["status"], "ready_for_engineering")

        # 3. Customer response draft
        cust_res = self.client.get("/api/ai/cases/CASE-2026-0891/customer-response")
        self.assertEqual(cust_res.status_code, 200)
        self.assertIn("Sarah", cust_res.json()["draft"])

    def test_auth_personas_and_switching(self):
        # 1. List personas
        res = self.client.get("/api/auth/personas")
        self.assertEqual(res.status_code, 200)
        personas = res.json()["personas"]
        self.assertEqual(len(personas), 3)

        # 2. Get current persona
        me_res = self.client.get("/api/auth/me")
        self.assertEqual(me_res.status_code, 200)
        self.assertIn("persona", me_res.json())
        self.assertIn("permissions", me_res.json())

        # 3. Switch persona to user-001 (Support Engineer)
        switch_res = self.client.post("/api/auth/switch/user-001")
        self.assertEqual(switch_res.status_code, 200)
        self.assertEqual(switch_res.json()["persona"]["id"], "user-001")
        self.assertIn("cases:read", switch_res.json()["permissions"])
        self.assertNotIn("system:reset", switch_res.json()["permissions"])

        # 4. Check roles list
        roles_res = self.client.get("/api/auth/roles")
        self.assertEqual(roles_res.status_code, 200)
        self.assertIn("support_engineer", roles_res.json())
        self.assertIn("support_lead", roles_res.json())
        self.assertIn("platform_engineer", roles_res.json())

    def test_assistant_case_qa(self):
        # Ask about Northstar webhook failure
        res = self.client.post(
            "/api/assistant/cases/CASE-2026-0891/ask",
            json={"question": "What is the root cause of this incident?"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["case_id"], "CASE-2026-0891")
        self.assertTrue(len(data["answer"]) > 10)
        self.assertIn("Webhook", data["answer"])

        # Ask about customer
        cust_q_res = self.client.post(
            "/api/assistant/cases/CASE-2026-0891/ask",
            json={"question": "Who is the customer and what is their SLA?"},
        )
        self.assertEqual(cust_q_res.status_code, 200)
        self.assertIn("Northstar Commerce", cust_q_res.json()["answer"])

    def test_settings_and_rbac_data_reset(self):
        # 1. System status
        status_res = self.client.get("/api/settings/status")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertIn("ai", status_data)
        self.assertIn("persona", status_data)
        self.assertIn("data", status_data)
        self.assertEqual(status_data["data"]["total_customers"], 5)

        # 2. Support Engineer cannot reset data (permission denied)
        self.client.post("/api/auth/switch/user-001")
        unauth_reset = self.client.post("/api/settings/reset-data")
        self.assertEqual(unauth_reset.status_code, 403)

        # 3. Switch to Platform Engineer (user-003) and reset data
        self.client.post("/api/auth/switch/user-003")
        auth_reset = self.client.post("/api/settings/reset-data")
        self.assertEqual(auth_reset.status_code, 200)
        self.assertTrue(auth_reset.json()["success"])
        self.assertEqual(auth_reset.json()["counts"]["customers"], 5)


if __name__ == "__main__":
    unittest.main()

