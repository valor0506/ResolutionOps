export type CustomerTier = 'Starter' | 'Growth' | 'Enterprise'

export type CaseStatus =
  | 'New'
  | 'Investigating'
  | 'Awaiting Customer'
  | 'Awaiting Engineering'
  | 'Fix In Progress'
  | 'Pending Verification'
  | 'Resolved'
  | 'Closed'

export type CasePriority = 'Low' | 'Medium' | 'High' | 'Critical'
export type CaseSeverity = 'Sev-1' | 'Sev-2' | 'Sev-3' | 'Sev-4'

export type EvidenceSource = 'customer' | 'system' | 'ai_hypothesis' | 'engineer'

export type EvidenceType =
  | 'customer_message'
  | 'internal_note'
  | 'sanitized_log'
  | 'api_trace'
  | 'kb_reference'
  | 'diagnostic_run'
  | 'verification_result'

export type HypothesisStatus = 'proposed' | 'investigating' | 'accepted' | 'rejected'
export type HandoffStatus = 'draft' | 'ready_for_engineering' | 'accepted'

export interface Customer {
  id: string
  name: string
  domain: string
  tier: CustomerTier
  sla_tier: string
  environment: string
  app_version: string
  primary_contact_name: string
  primary_contact_email: string
  created_at: string
  updated_at: string
  active_blockers: string[]
  known_commitments: string[]
}

export interface EvidenceRecord {
  id: string
  case_id: string
  source: EvidenceSource
  event_type: EvidenceType
  timestamp: string
  title: string
  content: string
  metadata: Record<string, unknown>
}

export interface DiagnosticHypothesis {
  id: string
  case_id: string
  rank: number
  title: string
  root_cause_explanation: string
  supporting_evidence: string[]
  contradictory_evidence: string[]
  confidence_score: number
  confidence_rationale: string
  recommended_test: string
  status: HypothesisStatus
  generated_at: string
}

export interface KnowledgeArticle {
  id: string
  title: string
  product_area: string
  description: string
  symptoms: string[]
  known_causes: string[]
  diagnostic_steps: string[]
  resolution_steps: string[]
  applicable_versions: string[]
  tags: string[]
  source: string
  updated_at: string
}

export interface EngineeringHandoff {
  id: string
  case_id: string
  problem_summary: string
  customer_impact: string
  affected_environment: string
  affected_version: string
  expected_behavior: string
  actual_behavior: string
  reproduction_steps: string[]
  timestamps: string[]
  request_ids: string[]
  sanitized_logs: string[]
  previous_troubleshooting: string
  suspected_root_cause: string
  supporting_evidence: string[]
  alternative_hypotheses: string[]
  missing_evidence: string[]
  suggested_next_steps: string[]
  severity_rationale: string
  suggested_owner_team: string
  acceptance_criteria: string[]
  is_complete: boolean
  status: HandoffStatus
  approved_by?: string | null
  approved_at?: string | null
  created_at: string
  updated_at: string
}

export interface VerificationCriterion {
  id: string
  description: string
  passed: boolean
  evidence?: string | null
  verified_at?: string | null
  verified_by?: string | null
}

export interface VerificationResult {
  id: string
  case_id: string
  criteria: VerificationCriterion[]
  all_passed: boolean
  approved_by?: string | null
  exception_documented?: string | null
  verified_at?: string | null
}

export interface Case {
  id: string
  title: string
  customer_id: string
  customer_name: string
  priority: CasePriority
  severity: CaseSeverity
  status: CaseStatus
  assigned_owner_id?: string | null
  assigned_owner_name?: string | null
  related_incident_id?: string | null
  current_blocker?: string | null
  next_action?: string | null

  // Structured issue report details
  summary: string
  symptoms: string[]
  expected_behavior: string
  actual_behavior: string
  reproduction_steps: string[]
  environment: string
  app_version?: string | null
  timestamps: string[]
  request_ids: string[]
  error_messages: string[]
  missing_information: string[]

  // Resolution attributes
  current_diagnosis?: string | null
  recommended_action?: string | null
  resolution_notes?: string | null
  customer_response_draft?: string | null

  created_at: string
  updated_at: string
}

export interface AuditRecord {
  id: string
  case_id: string
  action: string
  performed_by: string
  previous_state?: Record<string, unknown> | null
  new_state?: Record<string, unknown> | null
  reason?: string | null
  timestamp: string
}

export interface IntakeParseResponse {
  concise_summary: string
  suggested_customer_id?: string | null
  suggested_customer_name?: string | null
  expected_behavior?: string | null
  actual_behavior?: string | null
  known_reproduction_steps: string[]
  environment?: string | null
  available_timestamps: string[]
  request_ids: string[]
  error_evidence: string[]
  missing_information: string[]
  clarification_questions: string[]
  suggested_severity: CaseSeverity
  severity_rationale: string
  uncertainties: string[]
}

export interface DiagnosticToolExecutionResponse {
  tool_name: string
  execution_time_ms: number
  success: boolean
  summary: string
  data: unknown
  evidence_record_id?: string | null
}

// ============================================================================
// RBAC & Persona Types
// ============================================================================

export type UserRole = 'support_engineer' | 'support_lead' | 'platform_engineer'

export interface DemoPersona {
  id: string
  display_name: string
  email: string
  role: UserRole
  avatar_initials: string
  title: string
}

export interface PersonaListResponse {
  personas: DemoPersona[]
  active_persona_id: string
}

export interface CurrentPersonaResponse {
  persona: DemoPersona
  permissions: string[]
  role_display: string
}

// ============================================================================
// Conversational Assistant Types
// ============================================================================

export interface AssistantMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AskResponse {
  answer: string
  case_id: string
}

// ============================================================================
// Settings / System Status Types
// ============================================================================

export interface SystemStatus {
  ai: {
    gemini_available: boolean
    model: string
    provider: string
    mode: string
  }
  persona: {
    id: string
    display_name: string
    role: string
    title: string
  }
  data: {
    total_customers: number
    total_cases: number
    total_knowledge_articles: number
    is_demonstration_data: boolean
  }
}
