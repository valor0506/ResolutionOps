import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from server.models.schemas import DiagnosticToolExecutionResponse


# ============================================================================
# Synthetic Diagnostic Data Repositories
# ============================================================================

SYNTHETIC_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-98421": {
        "order_id": "ORD-98421",
        "customer_id": "cust-northstar",
        "customer_name": "Northstar Commerce",
        "created_at": "2026-10-18T04:15:22Z",
        "primary_db_status": "received",
        "read_replica_status": "received",
        "inventory_reserved": True,
        "total_amount": 1249.50,
        "currency": "USD",
        "buyer_email": "buyer.jennifer@example.com",
        "outbox_status": "FAILED_503_EXHAUSTED",
        "downstream_acknowledged": False,
        "items_count": 3,
        "idempotency_key": "idem-ord-98421-a1b2c3",
    },
    "ORD-98420": {
        "order_id": "ORD-98420",
        "customer_id": "cust-northstar",
        "customer_name": "Northstar Commerce",
        "created_at": "2026-10-18T03:50:11Z",
        "primary_db_status": "confirmed",
        "read_replica_status": "confirmed",
        "inventory_reserved": True,
        "total_amount": 89.00,
        "currency": "USD",
        "buyer_email": "buyer.mark@example.com",
        "outbox_status": "DELIVERED_200",
        "downstream_acknowledged": True,
        "items_count": 1,
        "idempotency_key": "idem-ord-98420-f9e8d7",
    },
}

SYNTHETIC_WEBHOOK_LOGS: List[Dict[str, Any]] = [
    {
        "id": "wh-log-001",
        "customer_id": "cust-northstar",
        "order_id": "ORD-98421",
        "event_type": "order.created",
        "target_url": "https://api.northstarcommerce.com/webhooks/orders",
        "attempt": 1,
        "max_attempts": 3,
        "timestamp": "2026-10-18T04:15:24Z",
        "http_status": 503,
        "latency_ms": 312,
        "response_headers": {
            "server": "cloudflare",
            "content-type": "text/html",
            "retry-after": "60",
            "cf-ray": "8d394a10c9-IAD",
        },
        "response_body_snippet": "<html><head><title>503 Service Temporarily Unavailable</title></head><body><h1>503 Service Unavailable</h1><p>The server is temporarily unable to service your request due to maintenance downtime or capacity problems.</p></body></html>",
        "egress_ip": "35.192.44.10",
        "idempotency_key": "idem-ord-98421-a1b2c3",
    },
    {
        "id": "wh-log-002",
        "customer_id": "cust-northstar",
        "order_id": "ORD-98421",
        "event_type": "order.created",
        "target_url": "https://api.northstarcommerce.com/webhooks/orders",
        "attempt": 2,
        "max_attempts": 3,
        "timestamp": "2026-10-18T04:16:24Z",
        "http_status": 503,
        "latency_ms": 289,
        "response_headers": {
            "server": "cloudflare",
            "content-type": "text/html",
            "retry-after": "240",
            "cf-ray": "8d394b29f1-IAD",
        },
        "response_body_snippet": "<html><head><title>503 Service Temporarily Unavailable</title></head><body><h1>503 Service Unavailable</h1></body></html>",
        "egress_ip": "35.192.44.11",
        "idempotency_key": "idem-ord-98421-a1b2c3",
    },
    {
        "id": "wh-log-003",
        "customer_id": "cust-northstar",
        "order_id": "ORD-98421",
        "event_type": "order.created",
        "target_url": "https://api.northstarcommerce.com/webhooks/orders",
        "attempt": 3,
        "max_attempts": 3,
        "timestamp": "2026-10-18T04:20:24Z",
        "http_status": 503,
        "latency_ms": 341,
        "response_headers": {
            "server": "cloudflare",
            "content-type": "text/html",
            "cf-ray": "8d394ff03a-IAD",
        },
        "response_body_snippet": "<html><head><title>503 Service Temporarily Unavailable</title></head><body><h1>503 Service Unavailable</h1></body></html>",
        "egress_ip": "35.192.44.10",
        "final_disposition": "MOVED_TO_DEAD_LETTER_QUEUE",
        "idempotency_key": "idem-ord-98421-a1b2c3",
    },
]

SYNTHETIC_APPLICATION_LOGS: List[Dict[str, Any]] = [
    {
        "timestamp": "2026-10-18T04:15:22.841Z",
        "level": "INFO",
        "service": "api-gateway",
        "trace_id": "trace-ord-99201-fe88",
        "request_id": "req-8849-a1fc-9920",
        "customer_id": "cust-northstar",
        "message": "POST /v2/orders - 200 OK - 142ms - payload_size=1840 bytes",
    },
    {
        "timestamp": "2026-10-18T04:15:23.110Z",
        "level": "INFO",
        "service": "order-service",
        "trace_id": "trace-ord-99201-fe88",
        "request_id": "req-8849-a1fc-9920",
        "customer_id": "cust-northstar",
        "message": "Order ORD-98421 transaction committed to Postgres primary. Inventory reserved for SKU-8841, SKU-1922.",
    },
    {
        "timestamp": "2026-10-18T04:15:23.240Z",
        "level": "INFO",
        "service": "event-bus",
        "trace_id": "trace-ord-99201-fe88",
        "request_id": "req-8849-a1fc-9920",
        "customer_id": "cust-northstar",
        "message": "Event 'order.created' published to Kafka topic 'order-lifecycle-events' [partition 4, offset 99281].",
    },
    {
        "timestamp": "2026-10-18T04:15:24.015Z",
        "level": "WARN",
        "service": "webhook-dispatcher",
        "trace_id": "trace-ord-99201-fe88",
        "request_id": "wh-attempt-1",
        "customer_id": "cust-northstar",
        "message": "Webhook dispatch to https://api.northstarcommerce.com/webhooks/orders failed with HTTP 503 (Attempt 1/3). Backoff scheduled for 60s.",
    },
    {
        "timestamp": "2026-10-18T04:16:24.330Z",
        "level": "WARN",
        "service": "webhook-dispatcher",
        "trace_id": "trace-ord-99201-fe88",
        "request_id": "wh-attempt-2",
        "customer_id": "cust-northstar",
        "message": "Webhook dispatch to https://api.northstarcommerce.com/webhooks/orders failed with HTTP 503 (Attempt 2/3). Backoff scheduled for 240s.",
    },
    {
        "timestamp": "2026-10-18T04:20:24.671Z",
        "level": "ERROR",
        "service": "webhook-dispatcher",
        "trace_id": "trace-ord-99201-fe88",
        "request_id": "wh-attempt-3",
        "customer_id": "cust-northstar",
        "message": "Webhook dispatch to https://api.northstarcommerce.com/webhooks/orders failed with HTTP 503 (Attempt 3/3). Retries exhausted. Message moved to DLQ 'dead-letter-webhooks'.",
    },
]


# ============================================================================
# Diagnostic Tool Implementations (Deterministic & Safe)
# ============================================================================

def execute_diagnostic_tool(
    tool_name: str, params: Dict[str, Any]
) -> DiagnosticToolExecutionResponse:
    """Dispatches a deterministic read-only diagnostic tool."""
    start_time = time.time()

    if tool_name == "get_order_status":
        order_id = params.get("order_id", "ORD-98421")
        order = SYNTHETIC_ORDERS.get(order_id)
        elapsed = int((time.time() - start_time) * 1000)

        if not order:
            return DiagnosticToolExecutionResponse(
                tool_name=tool_name,
                execution_time_ms=elapsed,
                success=False,
                summary=f"Order '{order_id}' was not found in synthetic database.",
                data={"searched_id": order_id, "found": False},
            )

        return DiagnosticToolExecutionResponse(
            tool_name=tool_name,
            execution_time_ms=elapsed,
            success=True,
            summary=(
                f"Order {order_id} primary DB status is '{order['primary_db_status']}', "
                f"inventory reserved: {order['inventory_reserved']}, "
                f"outbox status: '{order['outbox_status']}', "
                f"downstream acknowledged: {order['downstream_acknowledged']}."
            ),
            data=order,
        )

    elif tool_name == "inspect_webhook_logs":
        customer_id = params.get("customer_id", "cust-northstar")
        order_id = params.get("order_id")

        matched = [
            log
            for log in SYNTHETIC_WEBHOOK_LOGS
            if log["customer_id"] == customer_id
            and (not order_id or log.get("order_id") == order_id)
        ]
        elapsed = int((time.time() - start_time) * 1000)

        summary = (
            f"Found {len(matched)} webhook attempt records for customer '{customer_id}'. "
            f"All {len(matched)} attempts returned HTTP 503 Service Unavailable with Cloudflare response headers. "
            f"Final state: Dead Letter Queue (DLQ)."
        )

        return DiagnosticToolExecutionResponse(
            tool_name=tool_name,
            execution_time_ms=elapsed,
            success=True,
            summary=summary,
            data={"customer_id": customer_id, "total_attempts": len(matched), "logs": matched},
        )

    elif tool_name == "search_application_logs":
        query = params.get("query", "").lower()
        trace_id = params.get("trace_id")
        customer_id = params.get("customer_id")

        results = []
        for log in SYNTHETIC_APPLICATION_LOGS:
            if trace_id and log.get("trace_id") != trace_id:
                continue
            if customer_id and log.get("customer_id") != customer_id:
                continue
            if query and query not in log.get("message", "").lower() and query not in log.get("service", "").lower():
                continue
            results.append(log)

        elapsed = int((time.time() - start_time) * 1000)

        return DiagnosticToolExecutionResponse(
            tool_name=tool_name,
            execution_time_ms=elapsed,
            success=True,
            summary=f"Found {len(results)} matching log records across API Gateway, Order Service, and Webhook Dispatcher.",
            data={"match_count": len(results), "logs": results},
        )

    elif tool_name == "compare_source_and_downstream":
        order_id = params.get("order_id", "ORD-98421")
        order = SYNTHETIC_ORDERS.get(order_id)
        elapsed = int((time.time() - start_time) * 1000)

        if not order:
            return DiagnosticToolExecutionResponse(
                tool_name=tool_name,
                execution_time_ms=elapsed,
                success=False,
                summary=f"Order {order_id} not found for state reconciliation.",
                data={},
            )

        discrepancy = {
            "source_system": {
                "system": "PostgreSQL Primary Order Service",
                "status": "received",
                "inventory_reserved": True,
                "created_at": order["created_at"],
            },
            "downstream_system": {
                "system": "Northstar Customer Storefront & Merchant Dashboard",
                "reported_status": "Pending",
                "webhook_received": False,
                "discrepancy_detected": True,
                "root_cause_channel": "Downstream Webhook Notification Failure (503)",
            },
            "reconciliation_recommendation": (
                "Do NOT cancel or re-create order. Order exists safely in source DB. "
                "Reconcile by confirming customer webhook receiver health and triggering idempotent webhook replay."
            ),
        }

        return DiagnosticToolExecutionResponse(
            tool_name=tool_name,
            execution_time_ms=elapsed,
            success=True,
            summary="State divergence confirmed: Source DB has order in 'received' state, but downstream portal is 'Pending' due to missing webhook callback.",
            data=discrepancy,
        )

    elif tool_name == "probe_webhook_endpoint":
        url = params.get("url", "https://api.northstarcommerce.com/webhooks/orders")
        elapsed = int((time.time() - start_time) * 1000)

        # Simulated read-only health probe (safe test)
        probe_result = {
            "target_url": url,
            "probe_method": "HEAD",
            "probe_timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": 503,
            "status_text": "Service Unavailable",
            "response_time_ms": 320,
            "headers": {
                "server": "cloudflare",
                "cf-ray": "8d39f40019-IAD",
                "retry-after": "120",
            },
            "diagnosis": "Customer endpoint is still returning HTTP 503 via Cloudflare WAF or reverse proxy. Endpoint is NOT ready for replay.",
        }

        return DiagnosticToolExecutionResponse(
            tool_name=tool_name,
            execution_time_ms=elapsed,
            success=True,
            summary=f"Probe to {url} returned HTTP 503. Target endpoint is currently unavailable.",
            data=probe_result,
        )

    else:
        elapsed = int((time.time() - start_time) * 1000)
        return DiagnosticToolExecutionResponse(
            tool_name=tool_name,
            execution_time_ms=elapsed,
            success=False,
            summary=f"Unknown diagnostic tool '{tool_name}'. Available tools: get_order_status, inspect_webhook_logs, search_application_logs, compare_source_and_downstream, probe_webhook_endpoint.",
            data={},
        )

