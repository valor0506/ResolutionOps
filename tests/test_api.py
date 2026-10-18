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


if __name__ == "__main__":
    unittest.main()
