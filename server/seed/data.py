from datetime import datetime, timezone
from typing import Dict, List
from server.models.schemas import (
    Customer,
    CustomerTier,
    Case,
    CaseStatus,
    CasePriority,
    CaseSeverity,
    EvidenceRecord,
    EvidenceSource,
    EvidenceType,
    KnowledgeArticle,
    DiagnosticHypothesis,
    HypothesisStatus,
    EngineeringHandoff,
    HandoffStatus,
    VerificationResult,
    VerificationCriterion,
)

# ============================================================================
# Synthetic Customers
# ============================================================================

CUSTOMERS: List[Customer] = [
    Customer(
        id="cust-northstar",
        name="Northstar Commerce",
        domain="northstarcommerce.com",
        tier=CustomerTier.ENTERPRISE,
        sla_tier="99.99% (Sev-1: 15 min response)",
        environment="production (multi-tenant cluster-us-east-1)",
        app_version="3.4.2",
        primary_contact_name="Sarah Chen",
        primary_contact_email="schen@northstarcommerce.com",
        created_at=datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 18, 4, 30, tzinfo=timezone.utc),
        active_blockers=["Downstream order fulfillment stalled for batch ORD-98421"],
        known_commitments=[
            "Black Friday high-throughput SLA guarantee",
            "Custom webhook ingress IP whitelisting",
        ],
    ),
    Customer(
        id="cust-apex",
        name="Apex Logistics",
        domain="apexlogistics.io",
        tier=CustomerTier.GROWTH,
        sla_tier="99.9% (Sev-1: 1 hr response)",
        environment="production (cluster-eu-west-1)",
        app_version="3.3.8",
        primary_contact_name="Marcus Vance",
        primary_contact_email="mvance@apexlogistics.io",
        created_at=datetime(2025, 6, 15, 11, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 17, 14, 20, tzinfo=timezone.utc),
        active_blockers=["Morning automated dispatch jobs failing on 429 rate limits"],
        known_commitments=["Upcoming migration to v3.4.2 scheduled for next quarter"],
    ),
    Customer(
        id="cust-cloudscale",
        name="CloudScale Payments",
        domain="cloudscalepay.net",
        tier=CustomerTier.ENTERPRISE,
        sla_tier="99.99% (Sev-1: 15 min response)",
        environment="production (cluster-us-central-1)",
        app_version="3.4.2",
        primary_contact_name="Elena Rostova",
        primary_contact_email="erostova@cloudscalepay.net",
        created_at=datetime(2024, 11, 1, 8, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 18, 2, 10, tzinfo=timezone.utc),
        active_blockers=[],
        known_commitments=["PCI-DSS Level 1 compliance requirements"],
    ),
    Customer(
        id="cust-retailpulse",
        name="RetailPulse Analytics",
        domain="retailpulse.ai",
        tier=CustomerTier.STARTER,
        sla_tier="99.5% (Sev-1: 4 hr response)",
        environment="production (shared-us-west-2)",
        app_version="3.2.1",
        primary_contact_name="Dave K.",
        primary_contact_email="dave@retailpulse.ai",
        created_at=datetime(2025, 9, 20, 14, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 16, 18, 0, tzinfo=timezone.utc),
        active_blockers=[],
        known_commitments=[],
    ),
    Customer(
        id="cust-omnistack",
        name="OmniStack Media",
        domain="omnistackmedia.com",
        tier=CustomerTier.GROWTH,
        sla_tier="99.9% (Sev-1: 1 hr response)",
        environment="production (cluster-ap-southeast-1)",
        app_version="3.4.0",
        primary_contact_name="Kenji Sato",
        primary_contact_email="kenji@omnistackmedia.com",
        created_at=datetime(2025, 1, 12, 10, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 17, 8, 45, tzinfo=timezone.utc),
        active_blockers=["Webhook signature mismatches on payment callbacks"],
        known_commitments=["Single Sign-On (SAML) setup in progress"],
    ),
]


# ============================================================================
# Knowledge Base Articles (Runbooks & Architecture Docs)
# ============================================================================

KNOWLEDGE_ARTICLES: List[KnowledgeArticle] = [
    KnowledgeArticle(
        id="KB-001",
        title="Order State Lifecycle and Transition Invariants",
        product_area="Order Processing Engine",
        description="Comprehensive reference for order creation, state transitions, and event emission pipelines.",
        symptoms=[
            "Order remains in Pending state",
            "Status divergence between API response and merchant portal",
            "Inventory reserved but no confirmation email dispatched",
        ],
        known_causes=[
            "Event broker backlog or partition rebalancing delay",
            "Downstream webhook delivery failure preventing status callback",
            "Database read-replica replication lag (> 15 seconds)",
        ],
        diagnostic_steps=[
            "Query primary order database by order_id: SELECT id, status, updated_at FROM orders WHERE id = :id",
            "Inspect Outbox table for pending or failed webhook dispatch records",
            "Check event-broker consumer lag on 'order-lifecycle-events' topic",
        ],
        resolution_steps=[
            "If outbox message status is 'FAILED', check HTTP error code and retry policy",
            "If consumer lag is high, inspect partition health and scale consumer workers",
            "If read replica is lagging, point dashboard queries to primary for affected tenant",
        ],
        applicable_versions=["3.3.x", "3.4.x"],
        tags=["orders", "lifecycle", "architecture", "webhooks"],
        source="Core Engineering Runbooks",
        updated_at=datetime(2026, 8, 14, 12, 0, tzinfo=timezone.utc),
    ),
    KnowledgeArticle(
        id="KB-002",
        title="Webhook Delivery 503 Failures and Idempotent Event Replay",
        product_area="Integrations & Webhooks",
        description="Guidance for diagnosing downstream HTTP 503 errors during webhook delivery and safe replay procedures.",
        symptoms=[
            "Webhook delivery attempts exhausting retries",
            "HTTP 503 Service Unavailable recorded in dispatcher logs",
            "Customer reports their endpoint received no notifications despite our API returning 200",
        ],
        known_causes=[
            "Customer ingress firewall / WAF (e.g., Cloudflare, Akamai) rate limiting webhook workers",
            "Customer downstream service capacity exhaustion / crashing under load",
            "Network routing or DNS resolution failure for customer webhook URL",
        ],
        diagnostic_steps=[
            "Execute 'inspect_webhook_logs' with customer_id and event_type",
            "Verify customer webhook endpoint health via safe OPTIONS/HEAD probe",
            "Confirm idempotency key present in webhook header ('X-Idempotency-Key')",
            "Check historical cases for previous WAF blocking incidents on customer side",
        ],
        resolution_steps=[
            "Contact customer technical contact to verify endpoint availability and whitelist our egress IPs: 35.192.44.10, 35.192.44.11",
            "DO NOT blindly replay without verifying idempotency protection on the customer endpoint",
            "Once customer confirms readiness, trigger authorized idempotent replay via diagnostic workbench",
            "Record verification evidence and monitor retry response (expecting HTTP 200/202)",
        ],
        applicable_versions=["3.0.x", "3.1.x", "3.2.x", "3.3.x", "3.4.x"],
        tags=["webhooks", "503", "idempotency", "integrations", "runbook"],
        source="Platform Reliability Engineering",
        updated_at=datetime(2026, 9, 2, 16, 30, tzinfo=timezone.utc),
    ),
    KnowledgeArticle(
        id="KB-003",
        title="API Rate Limiting & Bucket Throttling Architecture",
        product_area="API Gateway",
        description="Explains sliding-window token bucket rate limits per subscription tier and handling 429 errors.",
        symptoms=[
            "HTTP 429 Too Many Requests returned to client",
            "Morning batch synchronization abruptly failing",
            "Headers 'X-RateLimit-Remaining: 0' and 'Retry-After' present in responses",
        ],
        known_causes=[
            "Client application launching parallel unthrottled worker threads",
            "Tier quota threshold exceeded (Starter: 60 rpm, Growth: 300 rpm, Enterprise: 3000 rpm)",
            "Shared API token reused across multiple worker clusters",
        ],
        diagnostic_steps=[
            "Inspect API Gateway request logs grouped by customer API key",
            "Analyze requests per minute distribution curve during peak window",
            "Check for Retry-After header adherence in client SDK logs",
        ],
        resolution_steps=[
            "Advise customer to implement exponential backoff with jitter in client client",
            "For Growth/Enterprise customers experiencing legitimate business spikes, request temporary rate limit increase",
        ],
        applicable_versions=["3.2.x", "3.3.x", "3.4.x"],
        tags=["rate-limiting", "429", "api-gateway", "limits"],
        source="API Infrastructure Team",
        updated_at=datetime(2026, 7, 19, 10, 15, tzinfo=timezone.utc),
    ),
    KnowledgeArticle(
        id="KB-004",
        title="JWT Token Rotation and Clock Skew Validation",
        product_area="Identity & Security",
        description="Handling public key rotation, caching delays, and client-side clock skew in JWT verification.",
        symptoms=[
            "Sudden 401 Unauthorized for all API calls after scheduled rotation",
            "Error: 'Signature verification failed' or 'Token issued in the future'",
        ],
        known_causes=[
            "JWKS key cache TTL on client side exceeds key propagation window",
            "Client server NTP synchronization drift > 300 seconds",
            "Using deprecated RS256 key after migration to Ed25519",
        ],
        diagnostic_steps=[
            "Extract 'kid' header from failing JWT token",
            "Compare 'kid' with current active keys at /.well-known/jwks.json",
            "Verify token 'nbf' and 'iat' against gateway server UTC time",
        ],
        resolution_steps=[
            "Clear stale JWKS cache on client SDK or restart client auth proxy",
            "Synchronize client server clock using standard chrony/NTP",
        ],
        applicable_versions=["3.4.x"],
        tags=["auth", "jwt", "security", "jwks", "401"],
        source="Security Engineering",
        updated_at=datetime(2026, 10, 5, 14, 0, tzinfo=timezone.utc),
    ),
]


# ============================================================================
# Synthetic Cases (10 realistic cases including the Flagship Incident)
# ============================================================================

CASES: List[Case] = [
    # --- Case 1: Flagship Incident ---
    Case(
        id="CASE-2026-0891",
        title="Order creation returns HTTP 200 but customer dashboard displays status as Pending",
        customer_id="cust-northstar",
        customer_name="Northstar Commerce",
        priority=CasePriority.CRITICAL,
        severity=CaseSeverity.SEV1,
        status=CaseStatus.INVESTIGATING,
        assigned_owner_id="usr-alex",
        assigned_owner_name="Alex Mercer (Support Lead)",
        related_incident_id="INC-2026-0104",
        current_blocker="Awaiting confirmation of downstream webhook retry failure root cause",
        next_action="Inspect webhook dispatcher log history for ORD-98421 and verify downstream 503 response",
        summary="Customer reports order #ORD-98421 was submitted via v2/orders API and returned HTTP 200 OK. However, the store admin portal and Northstar buyer portal continue showing the order status as 'Pending' for over 4 hours.",
        symptoms=[
            "API returned HTTP 200 with order_id ORD-98421",
            "Customer portal shows order status as 'Pending'",
            "Inventory reserved in primary DB but warehouse fulfillment has not been triggered",
            "Customer reports repeated customer service calls from end buyers",
        ],
        expected_behavior="Upon receiving HTTP 200 from POST /v2/orders, downstream status-update webhook should be received by Northstar's endpoint within 5 seconds, updating the dashboard to 'Confirmed'.",
        actual_behavior="Order remains stuck in 'Pending' state indefinitely. No webhook callback received by Northstar's systems.",
        reproduction_steps=[
            "1. Client application sends POST /v2/orders with valid payload for Northstar account",
            "2. Ingress API responds with HTTP 200 and body {'id': 'ORD-98421', 'status': 'received'}",
            "3. Inspect Northstar store dashboard at https://app.northstarcommerce.com/orders/ORD-98421",
            "4. Notice status remains 'Pending' indefinitely without progressing to 'Confirmed'",
        ],
        environment="production (multi-tenant cluster-us-east-1)",
        app_version="3.4.2",
        timestamps=[
            "2026-10-18T04:15:22Z (Client POST /v2/orders)",
            "2026-10-18T04:15:23Z (Gateway 200 OK response sent)",
            "2026-10-18T04:15:24Z (Webhook attempt #1: HTTP 503)",
            "2026-10-18T04:16:24Z (Webhook attempt #2: HTTP 503)",
            "2026-10-18T04:20:24Z (Webhook attempt #3: HTTP 503 - Final retry exhausted)",
        ],
        request_ids=[
            "req-8849-a1fc-9920",
            "trace-ord-99201-fe88",
            "evt-order-created-44810",
        ],
        error_messages=[
            "WebhookDispatcherError: Downstream endpoint https://api.northstarcommerce.com/webhooks/orders returned 503 Service Unavailable",
            "MaxRetriesExceeded: 3 attempts failed with backoff [60s, 240s]",
        ],
        missing_information=[
            "Current operational health of customer endpoint https://api.northstarcommerce.com/webhooks/orders",
            "Customer Cloudflare WAF block log for egress IP 35.192.44.10",
        ],
        current_diagnosis="Primary order ingestion succeeded, but asynchronous webhook delivery to Northstar's status callback endpoint failed with HTTP 503 (3 retries exhausted). The customer dashboard relies on this webhook callback to transition orders from Pending to Confirmed.",
        recommended_action="Execute diagnostic tool 'inspect_webhook_logs' to confirm 503 payloads. Advise customer technical contact to check their WAF/ingress capacity. Verify idempotency protection before initiating authorized replay.",
        resolution_notes="Investigation ongoing. Downstream 503 confirmed via synthetic gateway logs.",
        customer_response_draft="Hi Sarah, Our engineering team investigated order ORD-98421. The order was successfully written to our primary database, but our status webhook dispatched to your endpoint (https://api.northstarcommerce.com/webhooks/orders) encountered HTTP 503 Service Unavailable on all 3 delivery attempts. Could your infrastructure team confirm whether your webhook ingress was experiencing downtime or rate limiting around 04:15 UTC? Once confirmed, we are prepared to perform an idempotent replay.",
        created_at=datetime(2026, 10, 18, 5, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 18, 7, 30, tzinfo=timezone.utc),
    ),

    # --- Case 2: Apex Logistics Rate Limiting ---
    Case(
        id="CASE-2026-0885",
        title="Intermittent 429 Rate Limiting during morning batch dispatch jobs",
        customer_id="cust-apex",
        customer_name="Apex Logistics",
        priority=CasePriority.HIGH,
        severity=CaseSeverity.SEV2,
        status=CaseStatus.AWAITING_CUSTOMER,
        assigned_owner_id="usr-elena",
        assigned_owner_name="Elena Vance",
        related_incident_id=None,
        current_blocker="Waiting for customer to provide client-side concurrency configuration",
        next_action="Review worker concurrency counts sent by Marcus Vance",
        summary="Apex Logistics reports automated shipment dispatch scripts fail with HTTP 429 every weekday between 06:00 and 06:30 UTC.",
        symptoms=["HTTP 429 returned on POST /v2/shipments/batch", "Batch jobs abort with RateLimitExceededException"],
        expected_behavior="Batch jobs should complete smoothly within the Growth tier quota (300 requests/minute).",
        actual_behavior="Burst of 600 req/min at 06:00 UTC triggers token bucket exhaustion, resulting in 429 for subsequent calls.",
        reproduction_steps=["Run concurrent batch dispatch script with 20 parallel threads at 06:00 UTC"],
        environment="production (cluster-eu-west-1)",
        app_version="3.3.8",
        timestamps=["2026-10-17T06:00:15Z", "2026-10-17T06:01:00Z"],
        request_ids=["req-apex-7712", "req-apex-7713"],
        error_messages=["HTTP 429: Rate limit exceeded. Retry-After: 35"],
        missing_information=["Client-side thread pool size and retry backoff implementation details"],
        created_at=datetime(2026, 10, 17, 7, 10, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 17, 14, 0, tzinfo=timezone.utc),
    ),

    # --- Case 3: CloudScale Payments JWT Key Rotation ---
    Case(
        id="CASE-2026-0879",
        title="JWT signature verification failure following scheduled key rotation",
        customer_id="cust-cloudscale",
        customer_name="CloudScale Payments",
        priority=CasePriority.CRITICAL,
        severity=CaseSeverity.SEV1,
        status=CaseStatus.FIX_IN_PROGRESS,
        assigned_owner_id="usr-devin",
        assigned_owner_name="Devin Thorne (Platform Eng)",
        related_incident_id="INC-2026-0099",
        current_blocker="Stale JWKS cache on customer payment microservice",
        next_action="Monitor JWKS cache TTL expiry and confirm 200 OK on token exchange",
        summary="All API requests from CloudScale started failing with HTTP 401 after our 02:00 UTC automated JWKS key rotation.",
        symptoms=["401 Unauthorized across all endpoints", "Signature verification failed error"],
        expected_behavior="Customer services should fetch new public key from /.well-known/jwks.json automatically.",
        actual_behavior="Customer client library cached previous public key with 24-hour TTL and rejects tokens signed with new kid 'key-2026-10-b'.",
        reproduction_steps=["Send authenticated request using token signed with new rotation key"],
        environment="production (cluster-us-central-1)",
        app_version="3.4.2",
        timestamps=["2026-10-18T02:05:00Z", "2026-10-18T02:10:00Z"],
        request_ids=["req-csp-0012", "req-csp-0013"],
        error_messages=["jwt.exceptions.InvalidSignatureError: Signature verification failed"],
        missing_information=[],
        created_at=datetime(2026, 10, 18, 2, 15, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 18, 4, 0, tzinfo=timezone.utc),
    ),

    # --- Case 4: RetailPulse UTF-8 CSV BOM Corrupted Accents ---
    Case(
        id="CASE-2026-0870",
        title="Export CSV missing UTF-8 BOM causing corrupted accents in Excel",
        customer_id="cust-retailpulse",
        customer_name="RetailPulse Analytics",
        priority=CasePriority.LOW,
        severity=CaseSeverity.SEV4,
        status=CaseStatus.RESOLVED,
        assigned_owner_id="usr-alex",
        assigned_owner_name="Alex Mercer",
        related_incident_id=None,
        current_blocker=None,
        next_action="Case resolved and verified with customer",
        summary="Customer exported report with French and Spanish accents; characters showed as garbled 'Ã©' in Microsoft Excel.",
        symptoms=["Special characters rendered incorrectly in Excel"],
        expected_behavior="CSV export includes UTF-8 Byte Order Mark (BOM) so desktop Excel recognizes UTF-8 encoding.",
        actual_behavior="CSV was emitted as plain UTF-8 without BOM, causing Excel default Windows-1252 parsing.",
        reproduction_steps=["Export customer analytics report containing accented characters and open in Excel"],
        environment="production (shared-us-west-2)",
        app_version="3.2.1",
        timestamps=["2026-10-15T11:00:00Z"],
        request_ids=["req-rp-8819"],
        error_messages=[],
        missing_information=[],
        current_diagnosis="Missing UTF-8 BOM prefix (\\xef\\xbb\\xbf) on streaming CSV response header.",
        resolution_notes="Added BOM prefix to CSV streaming exporter. Verified in Excel 365 and Google Sheets.",
        created_at=datetime(2026, 10, 15, 11, 30, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 16, 16, 0, tzinfo=timezone.utc),
    ),

    # --- Case 5: OmniStack Webhook Signature Mismatch ---
    Case(
        id="CASE-2026-0865",
        title="Webhook signature validation failing with HMAC-SHA256 mismatch",
        customer_id="cust-omnistack",
        customer_name="OmniStack Media",
        priority=CasePriority.MEDIUM,
        severity=CaseSeverity.SEV3,
        status=CaseStatus.AWAITING_ENGINEERING,
        assigned_owner_id="usr-devin",
        assigned_owner_name="Devin Thorne",
        related_incident_id=None,
        current_blocker="Engineering reviewing webhook serializer whitespace normalization",
        next_action="Compare raw byte payload with HMAC calculated in customer receiver",
        summary="OmniStack webhook receiver rejects notifications because computed HMAC-SHA256 does not match 'X-Signature' header.",
        symptoms=["Customer webhook listener responds 403 Forbidden to valid events"],
        expected_behavior="Computed HMAC matches raw payload string bytes.",
        actual_behavior="Serializer introduced trailing newline in payload body before computing HMAC.",
        reproduction_steps=["Compute HMAC-SHA256 of payload with trailing newline vs without"],
        environment="production (cluster-ap-southeast-1)",
        app_version="3.4.0",
        timestamps=["2026-10-16T08:20:00Z"],
        request_ids=["req-omni-4401"],
        error_messages=["SignatureVerificationFailed: Provided header signature does not match computed digest"],
        missing_information=["Raw byte dump from customer ingress proxy"],
        created_at=datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 17, 8, 0, tzinfo=timezone.utc),
    ),

    # --- Case 6: Northstar Catalog Sync Timeout ---
    Case(
        id="CASE-2026-0858",
        title="Inventory sync batch timeout on catalogs exceeding 50,000 SKUs",
        customer_id="cust-northstar",
        customer_name="Northstar Commerce",
        priority=CasePriority.HIGH,
        severity=CaseSeverity.SEV2,
        status=CaseStatus.PENDING_VERIFICATION,
        assigned_owner_id="usr-devin",
        assigned_owner_name="Devin Thorne",
        related_incident_id="INC-2026-0084",
        current_blocker="Awaiting test run on staging environment with 65k catalog dataset",
        next_action="Execute verification script 'verify_catalog_batch_chunking'",
        summary="Nightly catalog sync for Northstar fails with gateway 504 Gateway Timeout when SKU count exceeds 50k.",
        symptoms=["504 Gateway Timeout on PUT /v2/catalog/sync", "Partial inventory update"],
        expected_behavior="Catalog sync processes asynchronously via chunked background workers.",
        actual_behavior="Sync was running synchronously in single HTTP request subject to 60s load balancer timeout.",
        reproduction_steps=["Upload 55,000 SKU JSON payload to PUT /v2/catalog/sync"],
        environment="production (multi-tenant cluster-us-east-1)",
        app_version="3.4.2",
        timestamps=["2026-10-14T23:05:00Z"],
        request_ids=["req-ns-catalog-01"],
        error_messages=["504 Gateway Timeout: Upstream server took longer than 60000ms"],
        missing_information=[],
        current_diagnosis="Synchronous batch processing violated gateway timeout envelope.",
        resolution_notes="Implemented streaming chunking worker. Fix deployed to staging.",
        created_at=datetime(2026, 10, 14, 23, 30, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 17, 18, 0, tzinfo=timezone.utc),
    ),

    # --- Case 7: Apex GraphQL Cursor Pagination ---
    Case(
        id="CASE-2026-0850",
        title="GraphQL pagination cursor returning duplicate records on page 4",
        customer_id="cust-apex",
        customer_name="Apex Logistics",
        priority=CasePriority.MEDIUM,
        severity=CaseSeverity.SEV3,
        status=CaseStatus.INVESTIGATING,
        assigned_owner_id="usr-elena",
        assigned_owner_name="Elena Vance",
        related_incident_id=None,
        current_blocker="Reproducing cursor tie-breaking sorting order on identical timestamps",
        next_action="Write test case in local harness for cursor sort tie-breaker",
        summary="Customer reports duplicate delivery records appearing when paginating deep into shipment history.",
        symptoms=["Same record appears at end of page 3 and beginning of page 4"],
        expected_behavior="Cursor pagination is strictly deterministic and non-overlapping.",
        actual_behavior="Multiple records share exact same 'created_at' millisecond without secondary ID sort tie-breaker.",
        reproduction_steps=["Query shipments with cursor after '2026-10-10T12:00:00.000Z'"],
        environment="production (cluster-eu-west-1)",
        app_version="3.3.8",
        timestamps=["2026-10-13T15:00:00Z"],
        request_ids=["req-apex-gql-99"],
        error_messages=[],
        missing_information=[],
        created_at=datetime(2026, 10, 13, 16, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 16, 11, 0, tzinfo=timezone.utc),
    ),

    # --- Case 8: CloudScale Idempotency Collision ---
    Case(
        id="CASE-2026-0842",
        title="Idempotency key collision returning cached stale transaction state",
        customer_id="cust-cloudscale",
        customer_name="CloudScale Payments",
        priority=CasePriority.HIGH,
        severity=CaseSeverity.SEV2,
        status=CaseStatus.RESOLVED,
        assigned_owner_id="usr-alex",
        assigned_owner_name="Alex Mercer",
        related_incident_id=None,
        current_blocker=None,
        next_action="Case resolved and post-mortem recorded",
        summary="Customer reused UUIDv4 idempotency key across different merchant accounts, causing cross-account payload collision.",
        symptoms=["Merchant A received transaction receipt belonging to Merchant B"],
        expected_behavior="Idempotency keys are scoped strictly to (tenant_id, account_id, idempotency_key).",
        actual_behavior="Redis idempotency key hash was only prefixed with 'idem:{key}' without tenant_id scoping.",
        reproduction_steps=["Submit duplicate idempotency key from two distinct tenant accounts"],
        environment="production (cluster-us-central-1)",
        app_version="3.4.2",
        timestamps=["2026-10-11T14:22:00Z"],
        request_ids=["req-csp-idem-1", "req-csp-idem-2"],
        error_messages=[],
        missing_information=[],
        current_diagnosis="Global Redis key collision due to missing tenant prefix in idempotency cache key.",
        resolution_notes="Scoped Redis cache key to 'idem:{tenant_id}:{key}'. Hotfix deployed and verified.",
        created_at=datetime(2026, 10, 11, 15, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 12, 19, 0, tzinfo=timezone.utc),
    ),

    # --- Case 9: RetailPulse Vague Complaint (Insufficient Evidence Example) ---
    Case(
        id="CASE-2026-0831",
        title="App is acting weird since yesterday — buttons not responding",
        customer_id="cust-retailpulse",
        customer_name="RetailPulse Analytics",
        priority=CasePriority.LOW,
        severity=CaseSeverity.SEV4,
        status=CaseStatus.AWAITING_CUSTOMER,
        assigned_owner_id="usr-alex",
        assigned_owner_name="Alex Mercer",
        related_incident_id=None,
        current_blocker="Customer has not replied to clarification questions regarding browser or specific page",
        next_action="Follow up with Dave K. if no response in 24 hours",
        summary="Customer submitted a 1-sentence ticket: 'The app is acting weird since yesterday, some buttons don't do anything when clicked.'",
        symptoms=["Vague: buttons not responding"],
        expected_behavior="Unknown — customer did not specify which page, workflow, or button.",
        actual_behavior="Unknown — no console logs, network errors, or timestamps provided.",
        reproduction_steps=["Unknown"],
        environment="production (shared-us-west-2)",
        app_version="3.2.1",
        timestamps=["Yesterday (unspecified)"],
        request_ids=[],
        error_messages=[],
        missing_information=[
            "Exact URL or navigation page where issue occurred",
            "Browser vendor and version (e.g. Chrome, Safari)",
            "Specific button clicked and expected action",
            "Any browser console errors or screenshot/video capture",
        ],
        created_at=datetime(2026, 10, 10, 17, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 11, 9, 0, tzinfo=timezone.utc),
    ),

    # --- Case 10: OmniStack Webhook Retry Timeout ---
    Case(
        id="CASE-2026-0820",
        title="Webhook retry backoff interval exceeds partner gateway timeout",
        customer_id="cust-omnistack",
        customer_name="OmniStack Media",
        priority=CasePriority.HIGH,
        severity=CaseSeverity.SEV2,
        status=CaseStatus.CLOSED,
        assigned_owner_id="usr-elena",
        assigned_owner_name="Elena Vance",
        related_incident_id="INC-2026-0062",
        current_blocker=None,
        next_action="Closed. Migration documentation delivered.",
        summary="Initial webhook backoff of 15 minutes caused partner order reconciliation timeouts.",
        symptoms=["Partner marked transactions as orphaned after 5 minutes of no webhook"],
        expected_behavior="Fast initial retries (10s, 30s, 60s) before long backoff.",
        actual_behavior="Linear 15-minute retry interval.",
        reproduction_steps=["Simulate initial 500 error on partner receiver"],
        environment="production (cluster-ap-southeast-1)",
        app_version="3.4.0",
        timestamps=["2026-10-08T09:00:00Z"],
        request_ids=["req-omni-retry-01"],
        error_messages=[],
        missing_information=[],
        current_diagnosis="Excessively slow retry cadence for time-critical media broadcast bookings.",
        resolution_notes="Updated retry policy to exponential backoff [10s, 30s, 90s, 300s]. Verified with partner.",
        created_at=datetime(2026, 10, 8, 10, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc),
    ),
]


# ============================================================================
# Synthetic Evidence Records for Case CASE-2026-0891 (The Flagship Incident)
# ============================================================================

CASE_EVIDENCE: Dict[str, List[EvidenceRecord]] = {
    "CASE-2026-0891": [
        EvidenceRecord(
            id="ev-001",
            case_id="CASE-2026-0891",
            source=EvidenceSource.CUSTOMER,
            event_type=EvidenceType.CUSTOMER_MESSAGE,
            timestamp=datetime(2026, 10, 18, 4, 45, tzinfo=timezone.utc),
            title="Initial Customer Escalation from Sarah Chen (Northstar)",
            content=(
                "URGENT: Order ORD-98421 was created via your REST API at 04:15 UTC. "
                "Our backend received a 200 OK response with the order ID. However, when checking "
                "our admin dashboard, the order has been stuck in 'Pending' for over 30 minutes! "
                "Our fulfillment pipeline is completely blocked and buyers are complaining. "
                "Please investigate immediately."
            ),
            metadata={
                "sender": "Sarah Chen <schen@northstarcommerce.com>",
                "channel": "Zendesk Escalation",
                "ticket_priority": "Urgent",
            },
        ),
        EvidenceRecord(
            id="ev-002",
            case_id="CASE-2026-0891",
            source=EvidenceSource.SYSTEM,
            event_type=EvidenceType.API_TRACE,
            timestamp=datetime(2026, 10, 18, 4, 15, 23, tzinfo=timezone.utc),
            title="API Gateway Access Log: POST /v2/orders (HTTP 200)",
            content=(
                "POST /v2/orders HTTP/1.1\n"
                "Host: api.resolutionops.internal\n"
                "X-Correlation-ID: req-8849-a1fc-9920\n"
                "X-Tenant-ID: cust-northstar\n"
                "Status: 200 OK\n"
                "Latency: 142ms\n"
                "Response Body: {\"id\": \"ORD-98421\", \"status\": \"received\", \"total\": 1249.50, \"currency\": \"USD\"}"
            ),
            metadata={
                "service": "api-gateway-us-east",
                "request_id": "req-8849-a1fc-9920",
                "client_ip": "198.51.100.42",
            },
        ),
        EvidenceRecord(
            id="ev-003",
            case_id="CASE-2026-0891",
            source=EvidenceSource.SYSTEM,
            event_type=EvidenceType.SANITIZED_LOG,
            timestamp=datetime(2026, 10, 18, 4, 15, 23, 500000, tzinfo=timezone.utc),
            title="Order Processing Service: Event Emission",
            content=(
                "[INFO] [OrderService] Order ORD-98421 committed to primary PostgreSQL. "
                "Event 'order.created' published to Kafka topic 'order-lifecycle-events' partition 4 offset 99281. "
                "Outbox record created for webhook delivery."
            ),
            metadata={
                "service": "order-service-pod-77b",
                "trace_id": "trace-ord-99201-fe88",
                "kafka_offset": 99281,
            },
        ),
        EvidenceRecord(
            id="ev-004",
            case_id="CASE-2026-0891",
            source=EvidenceSource.SYSTEM,
            event_type=EvidenceType.SANITIZED_LOG,
            timestamp=datetime(2026, 10, 18, 4, 15, 24, tzinfo=timezone.utc),
            title="Webhook Dispatcher Log: Attempt #1 Failed (HTTP 503)",
            content=(
                "[WARN] [WebhookDispatcher] Target: https://api.northstarcommerce.com/webhooks/orders\n"
                "Event: order.created (ORD-98421)\n"
                "Attempt: 1/3\n"
                "Response Code: 503 Service Unavailable\n"
                "Headers: Server: cloudflare, Retry-After: 60\n"
                "Body: <html><title>503 Service Temporarily Unavailable</title>...</html>\n"
                "Next Retry Scheduled: 2026-10-18T04:16:24Z"
            ),
            metadata={
                "dispatcher_worker": "worker-wh-03",
                "attempt": 1,
                "http_status": 503,
            },
        ),
        EvidenceRecord(
            id="ev-005",
            case_id="CASE-2026-0891",
            source=EvidenceSource.SYSTEM,
            event_type=EvidenceType.SANITIZED_LOG,
            timestamp=datetime(2026, 10, 18, 4, 20, 24, tzinfo=timezone.utc),
            title="Webhook Dispatcher Log: Attempt #3 Failed (Final Retry Exhausted)",
            content=(
                "[ERROR] [WebhookDispatcher] Target: https://api.northstarcommerce.com/webhooks/orders\n"
                "Event: order.created (ORD-98421)\n"
                "Attempt: 3/3 (FINAL)\n"
                "Response Code: 503 Service Unavailable\n"
                "Status: DEAD_LETTER_QUEUE\n"
                "Reason: Downstream webhook endpoint exhausted maximum retry threshold (3 attempts failed)."
            ),
            metadata={
                "dispatcher_worker": "worker-wh-01",
                "attempt": 3,
                "http_status": 503,
                "moved_to_dlq": True,
            },
        ),
        EvidenceRecord(
            id="ev-006",
            case_id="CASE-2026-0891",
            source=EvidenceSource.SYSTEM,
            event_type=EvidenceType.KB_REFERENCE,
            timestamp=datetime(2026, 10, 18, 5, 5, tzinfo=timezone.utc),
            title="Knowledge Base Correlated: KB-002",
            content=(
                "Correlated Runbook: KB-002 'Webhook Delivery 503 Failures and Idempotent Event Replay'. "
                "Recommends verifying downstream customer endpoint availability and checking customer Cloudflare WAF "
                "before initiating authorized idempotent replay."
            ),
            metadata={
                "kb_id": "KB-002",
                "confidence": 0.94,
            },
        ),
        EvidenceRecord(
            id="ev-007",
            case_id="CASE-2026-0891",
            source=EvidenceSource.ENGINEER,
            event_type=EvidenceType.INTERNAL_NOTE,
            timestamp=datetime(2026, 10, 18, 5, 20, tzinfo=timezone.utc),
            title="Internal Note from Alex Mercer (Support Lead)",
            content=(
                "Looking at historical incident INC-2025-0412, Northstar had an identical issue where their "
                "Cloudflare ingress rate-limiter blocked our webhook egress IP (35.192.44.10) after an automated "
                "ruleset update. We should not replay webhooks until Sarah's team whitelists our IPs, otherwise "
                "we risk another 503 dead-letter."
            ),
            metadata={
                "author": "Alex Mercer",
                "role": "Support Lead",
            },
        ),
    ]
}


# ============================================================================
# Initial Diagnostic Hypotheses for Case CASE-2026-0891
# ============================================================================

CASE_HYPOTHESES: Dict[str, List[DiagnosticHypothesis]] = {
    "CASE-2026-0891": [
        DiagnosticHypothesis(
            id="hyp-001",
            case_id="CASE-2026-0891",
            rank=1,
            title="Downstream Webhook Delivery Failure (HTTP 503) Exhausted Retries",
            root_cause_explanation=(
                "The order was successfully created in the primary database (ev-002, ev-003). "
                "However, the webhook dispatcher attempting to notify Northstar's endpoint "
                "(https://api.northstarcommerce.com/webhooks/orders) encountered HTTP 503 Service Unavailable "
                "across 3 retry attempts (ev-004, ev-005). Because Northstar's portal relies on this callback "
                "to transition the order state, the dashboard remains in 'Pending'."
            ),
            supporting_evidence=[
                "ev-002: Gateway returned 200 OK with order_id ORD-98421",
                "ev-003: OrderService committed order and published order.created event",
                "ev-004: Webhook dispatcher logged HTTP 503 on attempt 1",
                "ev-005: Webhook dispatcher logged HTTP 503 on final attempt 3 and moved message to DLQ",
                "KB-002: Runbook matches 503 downstream webhook retry exhaustion",
            ],
            contradictory_evidence=[
                "None found. All logs confirm successful internal ingestion and downstream dispatch failure.",
            ],
            confidence_score=0.92,
            confidence_rationale=(
                "Direct trace evidence exists in dispatcher logs showing exact 503 status code and exhausted retries. "
                "Matches previous incident INC-2025-0412 with Northstar Commerce."
            ),
            recommended_test="Execute diagnostic query 'inspect_webhook_logs' and test reachability of customer webhook receiver endpoint.",
            status=HypothesisStatus.ACCEPTED,
            generated_at=datetime(2026, 10, 18, 5, 10, tzinfo=timezone.utc),
        ),
        DiagnosticHypothesis(
            id="hyp-002",
            case_id="CASE-2026-0891",
            rank=2,
            title="Kafka Event Broker Consumer Partition Lag or Worker Crash",
            root_cause_explanation=(
                "Order created event was published by the ingress API, but the consumer group responsible for "
                "updating the read replica or triggering fulfillment crashed or experienced high lag."
            ),
            supporting_evidence=[
                "ev-003 confirms event was emitted to partition 4 offset 99281.",
            ],
            contradictory_evidence=[
                "ev-004 and ev-005 prove the consumer did consume the event and dispatched webhook attempts 1, 2, and 3. "
                "Therefore, the consumer worker was alive and processing.",
            ],
            confidence_score=0.18,
            confidence_rationale="Contradicted by dispatcher logs showing active delivery attempts.",
            recommended_test="Inspect consumer lag on partition 4.",
            status=HypothesisStatus.REJECTED,
            generated_at=datetime(2026, 10, 18, 5, 10, tzinfo=timezone.utc),
        ),
        DiagnosticHypothesis(
            id="hyp-003",
            case_id="CASE-2026-0891",
            rank=3,
            title="Database Read-Replica Replication Lag Delaying UI Query",
            root_cause_explanation=(
                "The dashboard query hit an out-of-sync PostgreSQL read replica that had not yet applied the "
                "transaction commit for ORD-98421."
            ),
            supporting_evidence=[
                "Divergence between customer-facing UI and API response.",
            ],
            contradictory_evidence=[
                "Replication lag on cluster-us-east-1 is currently 12ms (nominal < 50ms). Over 4 hours have elapsed, "
                "which completely rules out temporary replication lag.",
            ],
            confidence_score=0.05,
            confidence_rationale="Ruled out by 4+ hours elapsed time vs 12ms replica lag metrics.",
            recommended_test="Query read replica directly by order ID.",
            status=HypothesisStatus.REJECTED,
            generated_at=datetime(2026, 10, 18, 5, 10, tzinfo=timezone.utc),
        ),
    ]
}


# ============================================================================
# Engineering Handoff for CASE-2026-0891
# ============================================================================

CASE_HANDOFFS: Dict[str, EngineeringHandoff] = {
    "CASE-2026-0891": EngineeringHandoff(
        id="hnd-001",
        case_id="CASE-2026-0891",
        problem_summary="Order ORD-98421 returned HTTP 200 at API Gateway, but downstream status-update webhook received HTTP 503 from Northstar's endpoint across 3 retries, leaving dashboard in 'Pending'.",
        customer_impact="Northstar Commerce (Enterprise Tier) cannot fulfill order #ORD-98421 ($1,249.50). End customer experiencing fulfillment stall; SLA clock active (Sev-1).",
        affected_environment="production (multi-tenant cluster-us-east-1)",
        affected_version="3.4.2",
        expected_behavior="POST /v2/orders returns 200 and webhook delivery triggers downstream confirmation within 5 seconds.",
        actual_behavior="Webhook delivery returned HTTP 503 (Cloudflare WAF / endpoint capacity failure) on 3 attempts and moved to DLQ.",
        reproduction_steps=[
            "1. Inspect order ORD-98421 in primary DB: status is 'received'.",
            "2. Inspect Outbox DLQ table: record wh-ord-98421 present with status 'EXHAUSTED_503'.",
            "3. Query customer endpoint status via diagnostic runner.",
        ],
        timestamps=[
            "2026-10-18T04:15:22Z (Order Submitted)",
            "2026-10-18T04:15:24Z (Webhook Attempt 1: 503)",
            "2026-10-18T04:20:24Z (Webhook Attempt 3: 503 - DLQ)",
        ],
        request_ids=["req-8849-a1fc-9920", "trace-ord-99201-fe88"],
        sanitized_logs=[
            "POST /v2/orders 200 OK (142ms)",
            "[ERROR] [WebhookDispatcher] 503 Service Unavailable from https://api.northstarcommerce.com/webhooks/orders",
        ],
        previous_troubleshooting="Support verified order exists in primary DB. Correlated with historical incident INC-2025-0412 (Northstar Cloudflare rate limit).",
        suspected_root_cause="Northstar's webhook ingress receiver endpoint returned HTTP 503 due to customer-side capacity limits or Cloudflare WAF rule blocking our dispatcher egress IP (35.192.44.10).",
        supporting_evidence=[
            "Dispatcher log records with HTTP 503",
            "Cloudflare server response header in webhook response",
            "Customer report confirming no webhook arrived",
        ],
        alternative_hypotheses=[
            "Kafka consumer lag (rejected: dispatcher logs confirm consumption)",
            "Read-replica lag (rejected: nominal 12ms)",
        ],
        missing_evidence=[
            "Confirmation from Northstar DevOps that IP 35.192.44.10 is whitelisted and endpoint is healthy",
        ],
        suggested_next_steps=[
            "1. Coordinate with Northstar technical contact Sarah Chen to verify endpoint health.",
            "2. Once customer confirms readiness, trigger authorized idempotent replay for message wh-ord-98421.",
            "3. Verify order status transitions to 'Confirmed' on Northstar portal.",
        ],
        severity_rationale="Sev-1: Enterprise Tier customer with blocked fulfillment pipeline affecting high-value retail orders.",
        suggested_owner_team="Integrations & Platform Reliability Engineering",
        acceptance_criteria=[
            "Customer endpoint returns HTTP 200/202 upon idempotent replay",
            "Order status in primary DB and customer dashboard transitions to 'Confirmed'",
            "No duplicate charge or inventory reservation created",
        ],
        is_complete=True,
        status=HandoffStatus.READY_FOR_ENGINEERING,
        approved_by="Alex Mercer (Support Lead)",
        approved_at=datetime(2026, 10, 18, 5, 45, tzinfo=timezone.utc),
        created_at=datetime(2026, 10, 18, 5, 30, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 18, 5, 45, tzinfo=timezone.utc),
    )
}


# ============================================================================
# Verification Results for CASE-2026-0891
# ============================================================================

CASE_VERIFICATION: Dict[str, VerificationResult] = {
    "CASE-2026-0891": VerificationResult(
        id="vr-001",
        case_id="CASE-2026-0891",
        criteria=[
            VerificationCriterion(
                id="crit-1",
                description="Customer webhook receiver endpoint responds with HTTP 200/202 to health check probe",
                passed=False,
                evidence="Endpoint probe returned HTTP 503 during last diagnostic run at 05:22 UTC.",
                verified_at=datetime(2026, 10, 18, 5, 22, tzinfo=timezone.utc),
                verified_by="Alex Mercer",
            ),
            VerificationCriterion(
                id="crit-2",
                description="Downstream order record matches source primary DB record without duplicate inventory deductions",
                passed=False,
                evidence="Awaiting authorized idempotent replay after customer whitelisting.",
                verified_at=None,
                verified_by=None,
            ),
            VerificationCriterion(
                id="crit-3",
                description="Customer store dashboard displays status as 'Confirmed' for order ORD-98421",
                passed=False,
                evidence="Status currently remains 'Pending'.",
                verified_at=None,
                verified_by=None,
            ),
        ],
        all_passed=False,
        approved_by=None,
        exception_documented=None,
        verified_at=None,
    )
}
