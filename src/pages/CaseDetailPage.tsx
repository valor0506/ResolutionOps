import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Clock,
  Terminal,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Play,
  Copy,
  Check,
  Send,
  Sparkles,
  Layers,
  MessageSquare,
} from 'lucide-react'
import { apiFetch } from '../lib/api'
import type {
  Case,
  Customer,
  EvidenceRecord,
  DiagnosticHypothesis,
  EngineeringHandoff,
  VerificationResult,
  DiagnosticToolExecutionResponse,
} from '../types/domain'

export function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>()

  const [caseData, setCaseData] = useState<Case | null>(null)
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [evidence, setEvidence] = useState<EvidenceRecord[]>([])
  const [hypotheses, setHypotheses] = useState<DiagnosticHypothesis[]>([])
  const [handoff, setHandoff] = useState<EngineeringHandoff | null>(null)
  const [verification, setVerification] = useState<VerificationResult | null>(null)

  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'evidence' | 'diagnostics' | 'hypotheses' | 'handoff' | 'verification'>('evidence')

  // Diagnostic tool runner state
  const [selectedTool, setSelectedTool] = useState<string>('inspect_webhook_logs')
  const [runningTool, setRunningTool] = useState(false)
  const [toolResult, setToolResult] = useState<DiagnosticToolExecutionResponse | null>(null)

  // Internal note input
  const [noteText, setNoteText] = useState('')
  const [addingNote, setAddingNote] = useState(false)

  // Copy indicators
  const [copiedHandoff, setCopiedHandoff] = useState(false)
  const [copiedDraft, setCopiedDraft] = useState(false)

  // AI actions state
  const [investigatingWithAi, setInvestigatingWithAi] = useState(false)
  const [generatingHandoff, setGeneratingHandoff] = useState(false)
  const [customerDraft, setCustomerDraft] = useState<string>('')
  const [draftingResponse, setDraftingResponse] = useState(false)

  useEffect(() => {
    let ignore = false
    if (!caseId) return

    Promise.all([
      apiFetch<Case>(`/cases/${caseId}`),
      apiFetch<EvidenceRecord[]>(`/cases/${caseId}/evidence`).catch(() => []),
      apiFetch<DiagnosticHypothesis[]>(`/cases/${caseId}/hypotheses`).catch(() => []),
      apiFetch<EngineeringHandoff | null>(`/cases/${caseId}/handoff`).catch(() => null),
      apiFetch<VerificationResult | null>(`/cases/${caseId}/verification`).catch(() => null),
    ])
      .then(([c, ev, hyp, hnd, ver]) => {
        if (!ignore) {
          setCaseData(c)
          setEvidence(ev)
          setHypotheses(hyp)
          setHandoff(hnd)
          setVerification(ver)
          apiFetch<Customer>(`/customers/${c.customer_id}`)
            .then((cust) => {
              if (!ignore) setCustomer(cust)
            })
            .catch(() => null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          console.error('Failed to load case data:', err)
          setLoading(false)
        }
      })

    return () => {
      ignore = true
    }
  }, [caseId])

  const handleRunDiagnostic = async () => {
    if (!caseId) return
    setRunningTool(true)
    setToolResult(null)

    let params: Record<string, unknown> = {}
    if (selectedTool === 'get_order_status') {
      params = { order_id: 'ORD-98421' }
    } else if (selectedTool === 'inspect_webhook_logs') {
      params = { customer_id: caseData?.customer_id ?? 'cust-northstar', order_id: 'ORD-98421' }
    } else if (selectedTool === 'search_application_logs') {
      params = { query: '503', customer_id: caseData?.customer_id ?? 'cust-northstar' }
    } else if (selectedTool === 'compare_source_and_downstream') {
      params = { order_id: 'ORD-98421', customer_id: caseData?.customer_id ?? 'cust-northstar' }
    } else if (selectedTool === 'probe_webhook_endpoint') {
      params = { url: 'https://api.northstarcommerce.com/webhooks/orders', customer_id: caseData?.customer_id ?? 'cust-northstar' }
    }

    try {
      const res = await apiFetch<DiagnosticToolExecutionResponse>('/diagnostics/execute', {
        method: 'POST',
        body: JSON.stringify({
          tool_name: selectedTool,
          params,
          case_id: caseId,
        }),
      })
      setToolResult(res)
      // Refresh evidence timeline since diagnostic run was recorded
      const updatedEv = await apiFetch<EvidenceRecord[]>(`/cases/${caseId}/evidence`)
      setEvidence(updatedEv)
    } catch (err) {
      alert(`Diagnostic run failed: ${(err as Error).message}`)
    } finally {
      setRunningTool(false)
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!noteText.trim() || !caseId) return

    setAddingNote(true)
    try {
      await apiFetch<EvidenceRecord>(`/cases/${caseId}/evidence`, {
        method: 'POST',
        body: JSON.stringify({
          source: 'engineer',
          event_type: 'internal_note',
          title: 'Internal Engineering Note',
          content: noteText,
          metadata: { author: 'Current User' },
        }),
      })
      setNoteText('')
      const updatedEv = await apiFetch<EvidenceRecord[]>(`/cases/${caseId}/evidence`)
      setEvidence(updatedEv)
    } catch (err) {
      alert(`Failed to add note: ${(err as Error).message}`)
    } finally {
      setAddingNote(false)
    }
  }

  const handleHypothesisAction = async (hypId: string, newStatus: 'accepted' | 'rejected' | 'investigating') => {
    if (!caseId) return
    try {
      await apiFetch<DiagnosticHypothesis>(`/cases/${caseId}/hypotheses/${hypId}?status_val=${newStatus}`, {
        method: 'PATCH',
      })
      const updatedHyp = await apiFetch<DiagnosticHypothesis[]>(`/cases/${caseId}/hypotheses`)
      setHypotheses(updatedHyp)
    } catch (err) {
      alert(`Failed to update hypothesis: ${(err as Error).message}`)
    }
  }

  const handleAiInvestigate = async () => {
    if (!caseId) return
    setInvestigatingWithAi(true)
    try {
      const res = await apiFetch<{ case_id: string; hypotheses: DiagnosticHypothesis[] }>(
        `/ai/cases/${caseId}/investigate`,
        { method: 'POST' }
      )
      setHypotheses(res.hypotheses)
    } catch (err) {
      alert(`AI Investigation failed: ${(err as Error).message}`)
    } finally {
      setInvestigatingWithAi(false)
    }
  }

  const handleAiGenerateHandoff = async () => {
    if (!caseId) return
    setGeneratingHandoff(true)
    try {
      const res = await apiFetch<EngineeringHandoff>(`/ai/cases/${caseId}/generate-handoff`, {
        method: 'POST',
      })
      setHandoff(res)
    } catch (err) {
      alert(`AI Handoff Generation failed: ${(err as Error).message}`)
    } finally {
      setGeneratingHandoff(false)
    }
  }

  const handleDraftCustomerResponse = async () => {
    if (!caseId) return
    setDraftingResponse(true)
    try {
      const res = await apiFetch<{ case_id: string; draft: string }>(
        `/ai/cases/${caseId}/customer-response`
      )
      setCustomerDraft(res.draft)
    } catch (err) {
      alert(`Drafting response failed: ${(err as Error).message}`)
    } finally {
      setDraftingResponse(false)
    }
  }

  const handleCopyHandoff = () => {
    if (!handoff) return
    const text = `# Engineering Handoff — ${caseData?.id}: ${caseData?.title}
**Customer Impact:** ${handoff.customer_impact}
**Affected Environment:** ${handoff.affected_environment} (${handoff.affected_version})
**Expected Behavior:** ${handoff.expected_behavior}
**Actual Behavior:** ${handoff.actual_behavior}

## Suspected Root Cause
${handoff.suspected_root_cause}

## Supporting Evidence
${handoff.supporting_evidence.map((s) => `- ${s}`).join('\n')}

## Reproduction Steps
${handoff.reproduction_steps.map((s) => s).join('\n')}

## Recommended Next Steps
${handoff.suggested_next_steps.map((s) => `- ${s}`).join('\n')}

## Verification & Acceptance Criteria
${handoff.acceptance_criteria.map((c) => `- [ ] ${c}`).join('\n')}
`
    navigator.clipboard.writeText(text)
    setCopiedHandoff(true)
    setTimeout(() => setCopiedHandoff(false), 2000)
  }

  const handleCopyCustomerDraft = () => {
    if (!customerDraft) return
    navigator.clipboard.writeText(customerDraft)
    setCopiedDraft(true)
    setTimeout(() => setCopiedDraft(false), 2000)
  }

  if (loading) {
    return (
      <div className="p-8 max-w-7xl animate-pulse space-y-6">
        <div className="h-6 w-32 bg-slate-200 rounded" />
        <div className="h-20 bg-white rounded-xl border border-slate-200" />
        <div className="grid grid-cols-3 gap-6">
          <div className="h-96 bg-white rounded-xl border border-slate-200" />
          <div className="col-span-2 h-96 bg-white rounded-xl border border-slate-200" />
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="p-8 max-w-7xl">
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
          <AlertTriangle className="h-10 w-10 text-amber-500 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900">Case Not Found</h2>
          <p className="text-xs text-slate-500 mt-1">The requested case {caseId} does not exist.</p>
          <Link to="/cases" className="mt-4 inline-block text-xs font-semibold text-blue-600 underline">
            Return to Case List
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl">
      {/* Top Breadcrumb & Status Bar */}
      <div className="mb-6">
        <Link to="/cases" className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors mb-3">
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Cases
        </Link>

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200/80 pb-5">
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-mono text-sm font-bold text-slate-900">{caseData.id}</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                {caseData.priority} / {caseData.severity}
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200">
                Status: {caseData.status}
              </span>
              {caseData.related_incident_id && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-purple-50 text-purple-700 border border-purple-200">
                  Incident: {caseData.related_incident_id}
                </span>
              )}
            </div>
            <h1 className="text-xl font-semibold text-slate-900 tracking-tight mt-1.5">
              {caseData.title}
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Customer: <strong className="text-slate-800">{caseData.customer_name}</strong> • Assigned: {caseData.assigned_owner_name ?? 'Unassigned'}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setActiveTab('diagnostics')}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-3.5 py-2 text-xs font-medium text-white hover:bg-slate-800 transition-colors shadow-xs"
            >
              <Terminal className="h-3.5 w-3.5 text-blue-400" />
              Diagnostic Workbench
            </button>
            <button
              onClick={() => setActiveTab('handoff')}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <FileText className="h-3.5 w-3.5 text-slate-500" />
              Engineering Handoff
            </button>
          </div>
        </div>
      </div>

      {/* Grid Layout: Left Column (Context & Issue) + Right Column (Investigation Workspace) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 cols): Customer Context & Issue Report */}
        <div className="lg:col-span-5 space-y-6">
          {/* Customer Context Card */}
          <div className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-xs">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
              <Layers className="h-4 w-4 text-blue-600" />
              Customer Context & Environment
            </h2>
            {customer ? (
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Tier & SLA</span>
                  <span className="font-medium text-slate-800">{customer.tier} ({customer.sla_tier})</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Environment</span>
                  <span className="font-mono text-slate-800">{customer.environment}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">App Version</span>
                  <span className="font-mono font-medium text-slate-800">v{customer.app_version}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Technical Lead</span>
                  <span className="text-slate-800">{customer.primary_contact_name} ({customer.primary_contact_email})</span>
                </div>
                {customer.active_blockers.length > 0 && (
                  <div className="pt-1">
                    <span className="text-rose-700 font-semibold block mb-1">Active Blocker:</span>
                    <p className="text-slate-700 bg-rose-50 border border-rose-200 rounded p-2 text-[11px]">
                      {customer.active_blockers[0]}
                    </p>
                  </div>
                )}
                <div className="pt-1">
                  <span className="text-slate-500 block mb-1">Historical Cross-Reference:</span>
                  <p className="text-slate-600 bg-slate-50 border border-slate-200 rounded p-2 text-[11px]">
                    INC-2025-0412: Previous Cloudflare WAF 503 block on egress IP 35.192.44.10 resolved after whitelisting.
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">Loading customer context...</p>
            )}
          </div>

          {/* Issue Report Card */}
          <div className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <FileText className="h-4 w-4 text-purple-600" />
              Structured Issue Report
            </h2>

            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Summary</span>
              <p className="text-xs text-slate-800 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                {caseData.summary}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-emerald-50/60 border border-emerald-200/60 p-2.5 rounded-lg">
                <span className="font-semibold text-emerald-800 block mb-0.5">Expected Behavior</span>
                <p className="text-slate-700 text-[11px]">{caseData.expected_behavior}</p>
              </div>
              <div className="bg-rose-50/60 border border-rose-200/60 p-2.5 rounded-lg">
                <span className="font-semibold text-rose-800 block mb-0.5">Actual Behavior</span>
                <p className="text-slate-700 text-[11px]">{caseData.actual_behavior}</p>
              </div>
            </div>

            {/* Reproduction Steps */}
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Reproduction Steps
              </span>
              <ol className="list-decimal list-inside space-y-1 text-xs text-slate-700">
                {caseData.reproduction_steps.map((step, idx) => (
                  <li key={idx} className="leading-relaxed">{step}</li>
                ))}
              </ol>
            </div>

            {/* Request IDs & Correlation Traces */}
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Correlation Traces & Request IDs
              </span>
              <div className="flex flex-wrap gap-1.5">
                {caseData.request_ids.map((id) => (
                  <span key={id} className="font-mono text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                    {id}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Diagnostic Info */}
            {caseData.missing_information.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 p-3 rounded-lg">
                <div className="flex items-center gap-1.5 text-amber-800 font-semibold text-xs mb-1">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Missing Diagnostic Evidence
                </div>
                <ul className="list-disc list-inside space-y-0.5 text-[11px] text-amber-900">
                  {caseData.missing_information.map((m, idx) => (
                    <li key={idx}>{m}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (7 cols): Investigation Tabs (Evidence, Diagnostics, Hypotheses, Handoff, Verification) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Tab Navigation */}
          <div className="flex border-b border-slate-200 bg-white rounded-t-xl px-2 pt-2 gap-1 overflow-x-auto">
            <button
              onClick={() => setActiveTab('evidence')}
              className={`px-3 py-2 text-xs font-medium rounded-t-lg border-b-2 transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === 'evidence'
                  ? 'border-blue-600 text-blue-600 bg-blue-50/40'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Clock className="h-3.5 w-3.5" />
              Evidence Timeline ({evidence.length})
            </button>
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`px-3 py-2 text-xs font-medium rounded-t-lg border-b-2 transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === 'diagnostics'
                  ? 'border-blue-600 text-blue-600 bg-blue-50/40'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Terminal className="h-3.5 w-3.5" />
              Diagnostic Tools
            </button>
            <button
              onClick={() => setActiveTab('hypotheses')}
              className={`px-3 py-2 text-xs font-medium rounded-t-lg border-b-2 transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === 'hypotheses'
                  ? 'border-blue-600 text-blue-600 bg-blue-50/40'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Sparkles className="h-3.5 w-3.5 text-blue-600" />
              Hypotheses ({hypotheses.length})
            </button>
            <button
              onClick={() => setActiveTab('handoff')}
              className={`px-3 py-2 text-xs font-medium rounded-t-lg border-b-2 transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === 'handoff'
                  ? 'border-blue-600 text-blue-600 bg-blue-50/40'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <FileText className="h-3.5 w-3.5" />
              Engineering Handoff
            </button>
            <button
              onClick={() => setActiveTab('verification')}
              className={`px-3 py-2 text-xs font-medium rounded-t-lg border-b-2 transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === 'verification'
                  ? 'border-blue-600 text-blue-600 bg-blue-50/40'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              Resolution & Verification
            </button>
          </div>

          {/* TAB 1: EVIDENCE TIMELINE */}
          {activeTab === 'evidence' && (
            <div className="rounded-b-xl rounded-tr-xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Correlated Evidence Timeline</h3>
                  <p className="text-xs text-slate-500">
                    Timestamped audit events, customer messages, API traces, sanitized logs, and runbooks.
                  </p>
                </div>
              </div>

              {/* Timeline Events List */}
              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {evidence.map((ev) => (
                  <div key={ev.id} className="relative group">
                    {/* Circle Node */}
                    <div
                      className={`absolute -left-[27px] top-1.5 h-3.5 w-3.5 rounded-full border-2 bg-white ${
                        ev.source === 'customer'
                          ? 'border-blue-500'
                          : ev.source === 'engineer'
                          ? 'border-purple-500'
                          : ev.event_type === 'diagnostic_run'
                          ? 'border-emerald-500'
                          : 'border-slate-400'
                      }`}
                    />

                    <div className="rounded-lg border border-slate-200/80 bg-slate-50/50 p-3.5 hover:border-slate-300 transition-colors">
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-xs text-slate-900">{ev.title}</span>
                          <span
                            className={`text-[9px] font-semibold uppercase px-1.5 py-0.2 rounded ${
                              ev.source === 'customer'
                                ? 'bg-blue-100 text-blue-700'
                                : ev.source === 'engineer'
                                ? 'bg-purple-100 text-purple-700'
                                : 'bg-slate-200 text-slate-700'
                            }`}
                          >
                            {ev.source} • {ev.event_type}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400">
                          {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} UTC
                        </span>
                      </div>

                      <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                        {ev.content}
                      </pre>

                      {Object.keys(ev.metadata).length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-200/60 flex flex-wrap gap-2 text-[10px] text-slate-500 font-mono">
                          {Object.entries(ev.metadata).map(([k, v]) => (
                            <span key={k} className="bg-white px-1.5 py-0.5 rounded border border-slate-200">
                              {k}: {String(v)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Add Internal Note */}
              <form onSubmit={handleAddNote} className="pt-4 border-t border-slate-100">
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Append Internal Note / Observation
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    placeholder="Document test results, customer conversation, or diagnostic findings..."
                    className="flex-1 rounded-lg border border-slate-200 py-2 px-3 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                  <button
                    type="submit"
                    disabled={addingNote || !noteText.trim()}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3.5 py-2 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50"
                  >
                    <Send className="h-3 w-3" />
                    Record Note
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* TAB 2: DIAGNOSTIC TOOLS WORKBENCH */}
          {activeTab === 'diagnostics' && (
            <div className="rounded-b-xl rounded-tr-xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Deterministic Diagnostic Workbench</h3>
                <p className="text-xs text-slate-500">
                  Run safe, read-only diagnostic queries against synthetic databases, dispatcher queues, and log stores.
                  Outputs are automatically appended to the case evidence timeline.
                </p>
              </div>

              {/* Tool Selector & Run Button */}
              <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
                <label className="block text-xs font-semibold text-slate-700">Select Diagnostic Query</label>
                <div className="flex flex-col sm:flex-row gap-2">
                  <select
                    value={selectedTool}
                    onChange={(e) => setSelectedTool(e.target.value)}
                    className="flex-1 rounded-lg border border-slate-200 bg-white py-2 px-3 text-xs text-slate-800 font-medium"
                  >
                    <option value="inspect_webhook_logs">inspect_webhook_logs (Inspect 503 delivery failures & retry attempts)</option>
                    <option value="get_order_status">get_order_status (Query primary DB vs replica vs outbox state)</option>
                    <option value="search_application_logs">search_application_logs (Search gateway & service logs for 503)</option>
                    <option value="compare_source_and_downstream">compare_source_and_downstream (Reconcile state divergence)</option>
                    <option value="probe_webhook_endpoint">probe_webhook_endpoint (Safe read-only probe of customer receiver)</option>
                  </select>
                  <button
                    onClick={handleRunDiagnostic}
                    disabled={runningTool}
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition-colors shadow-xs disabled:opacity-50"
                  >
                    <Play className="h-3.5 w-3.5" />
                    {runningTool ? 'Executing...' : 'Run Query'}
                  </button>
                </div>
              </div>

              {/* Tool Result Display */}
              {toolResult && (
                <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-slate-900">
                      Query Result: {toolResult.tool_name}
                    </span>
                    <span className="text-[11px] font-mono text-slate-500">
                      {toolResult.execution_time_ms}ms • Recorded to Evidence
                    </span>
                  </div>

                  <p className="text-xs text-slate-800 bg-blue-50/60 border border-blue-200/60 p-2.5 rounded-lg font-medium">
                    {toolResult.summary}
                  </p>

                  <pre className="text-[11px] font-mono bg-slate-900 text-slate-200 p-3.5 rounded-lg overflow-x-auto max-h-72">
                    {JSON.stringify(toolResult.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: DIAGNOSTIC HYPOTHESES */}
          {activeTab === 'hypotheses' && (
            <div className="rounded-b-xl rounded-tr-xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-6">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Ranked Root-Cause Hypotheses</h3>
                  <p className="text-xs text-slate-500">
                    Grounded hypotheses synthesized from available traces, logs, and customer history.
                  </p>
                </div>
                <button
                  onClick={handleAiInvestigate}
                  disabled={investigatingWithAi}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-700 hover:bg-blue-100 disabled:opacity-50 transition-colors shadow-xs"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  {investigatingWithAi ? 'Synthesizing with Gemini...' : 'AI Re-Investigate'}
                </button>
              </div>

              <div className="space-y-4">
                {hypotheses.map((hyp) => (
                  <div
                    key={hyp.id}
                    className={`rounded-xl border p-4.5 space-y-3 transition-colors ${
                      hyp.status === 'accepted'
                        ? 'border-emerald-300 bg-emerald-50/20'
                        : hyp.status === 'rejected'
                        ? 'border-slate-200 bg-slate-50/50 opacity-70'
                        : 'border-slate-200 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                          #{hyp.rank}
                        </span>
                        <h4 className="text-xs font-semibold text-slate-900">{hyp.title}</h4>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-slate-600">
                          Confidence: <strong className="text-slate-900">{Math.round(hyp.confidence_score * 100)}%</strong>
                        </span>
                        <span
                          className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full ${
                            hyp.status === 'accepted'
                              ? 'bg-emerald-100 text-emerald-800'
                              : hyp.status === 'rejected'
                              ? 'bg-slate-200 text-slate-700'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {hyp.status}
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-700 leading-relaxed">
                      {hyp.root_cause_explanation}
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
                      <div className="bg-emerald-50/50 border border-emerald-200/50 p-2.5 rounded-lg">
                        <span className="font-semibold text-emerald-900 block mb-1">Supporting Evidence</span>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-700">
                          {hyp.supporting_evidence.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="bg-rose-50/50 border border-rose-200/50 p-2.5 rounded-lg">
                        <span className="font-semibold text-rose-900 block mb-1">Contradictory / Unknowns</span>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-700">
                          {hyp.contradictory_evidence.map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-2.5 rounded-lg text-[11px] text-slate-600">
                      <strong>Recommended Diagnostic Test:</strong> {hyp.recommended_test}
                    </div>

                    <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-100">
                      <button
                        onClick={() => handleHypothesisAction(hyp.id, 'rejected')}
                        className="px-3 py-1 rounded text-xs font-medium text-slate-600 hover:bg-slate-100"
                      >
                        Reject Hypothesis
                      </button>
                      <button
                        onClick={() => handleHypothesisAction(hyp.id, 'accepted')}
                        className="px-3 py-1 rounded bg-emerald-600 text-xs font-medium text-white hover:bg-emerald-700"
                      >
                        Accept as Working Diagnosis
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: ENGINEERING HANDOFF */}
          {activeTab === 'handoff' && (
            <div className="rounded-b-xl rounded-tr-xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-6">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Structured Engineering Handoff</h3>
                  <p className="text-xs text-slate-500">
                    Comprehensive technical dossier for escalating to core engineering or platform reliability.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleAiGenerateHandoff}
                    disabled={generatingHandoff}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-blue-50 border border-blue-200 px-3 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-100 disabled:opacity-50 transition-colors"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                    {generatingHandoff ? 'Regenerating...' : 'Regenerate with AI'}
                  </button>
                  <button
                    onClick={handleCopyHandoff}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    {copiedHandoff ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                    {copiedHandoff ? 'Copied Markdown' : 'Copy Handoff'}
                  </button>
                </div>
              </div>

              {handoff ? (
                <div className="space-y-4 text-xs">
                  <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
                    <span className="font-semibold text-slate-900 block">Problem Summary & Customer Impact</span>
                    <p className="text-slate-700">{handoff.problem_summary}</p>
                    <p className="text-rose-700 font-medium">{handoff.customer_impact}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="border border-slate-200 p-3 rounded-lg">
                      <span className="font-semibold text-slate-700 block mb-1">Suspected Root Cause</span>
                      <p className="text-slate-600 text-[11px] leading-relaxed">{handoff.suspected_root_cause}</p>
                    </div>
                    <div className="border border-slate-200 p-3 rounded-lg">
                      <span className="font-semibold text-slate-700 block mb-1">Target Engineering Team</span>
                      <p className="text-slate-600 text-[11px] font-medium">{handoff.suggested_owner_team}</p>
                    </div>
                  </div>

                  <div className="border border-slate-200 p-3 rounded-lg space-y-2">
                    <span className="font-semibold text-slate-700 block">Suggested Next Diagnostic Steps</span>
                    <ul className="list-decimal list-inside space-y-1 text-slate-600 text-[11px]">
                      {handoff.suggested_next_steps.map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="border border-emerald-200 bg-emerald-50/30 p-3.5 rounded-lg space-y-2">
                    <span className="font-semibold text-emerald-900 block">Acceptance & Verification Criteria</span>
                    <ul className="list-disc list-inside space-y-1 text-slate-700 text-[11px]">
                      {handoff.acceptance_criteria.map((c, idx) => (
                        <li key={idx}>{c}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400">No handoff created yet.</p>
              )}
            </div>
          )}

          {/* TAB 5: RESOLUTION & VERIFICATION GATE */}
          {activeTab === 'verification' && (
            <div className="rounded-b-xl rounded-tr-xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Resolution Verification Gate</h3>
                <p className="text-xs text-slate-500">
                  Cases cannot be marked Resolved simply because an AI generated a response.
                  Mandatory verification criteria must be recorded and signed off by an authorized human.
                </p>
              </div>

              {verification ? (
                <div className="space-y-4">
                  <div className="space-y-3">
                    {verification.criteria.map((crit) => (
                      <div
                        key={crit.id}
                        className={`rounded-xl border p-4 flex items-start gap-3.5 ${
                          crit.passed ? 'border-emerald-300 bg-emerald-50/30' : 'border-amber-200 bg-amber-50/20'
                        }`}
                      >
                        <div className="pt-0.5">
                          {crit.passed ? (
                            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-amber-500" />
                          )}
                        </div>
                        <div className="flex-1 text-xs">
                          <p className="font-semibold text-slate-900">{crit.description}</p>
                          <p className="text-[11px] text-slate-600 mt-1">
                            Evidence: <span className="font-mono">{crit.evidence ?? 'Pending test run'}</span>
                          </p>
                          {crit.verified_by && (
                            <p className="text-[10px] text-slate-400 mt-0.5">
                              Verified by: {crit.verified_by}
                            </p>
                          )}
                        </div>
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                            crit.passed ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {crit.passed ? 'PASSED' : 'UNVERIFIED'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-2">
                    <span className="text-xs font-semibold text-slate-900 block">Closure Authorization</span>
                    <p className="text-xs text-slate-500">
                      All criteria must pass before moving case to Resolved. Alternatively, an authorized lead must document an explicit exception.
                    </p>
                    <div className="flex items-center gap-2 pt-2">
                      <button
                        disabled={!verification.all_passed}
                        className="px-4 py-2 rounded-lg bg-emerald-600 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
                      >
                        Approve Case Closure & Mark Resolved
                      </button>
                    </div>
                  </div>

                  {/* Customer Response Draft Generator */}
                  <div className="rounded-xl border border-slate-200 bg-white p-5 space-y-3 pt-6 border-t border-slate-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 text-blue-600" />
                        <h4 className="text-xs font-semibold text-slate-900">Grounded Customer Response Draft</h4>
                      </div>
                      <button
                        onClick={handleDraftCustomerResponse}
                        disabled={draftingResponse}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-100 transition-colors disabled:opacity-50"
                      >
                        <Sparkles className="h-3 w-3" />
                        {draftingResponse ? 'Drafting...' : 'Draft with Gemini'}
                      </button>
                    </div>

                    <p className="text-xs text-slate-500">
                      AI drafts a technical update citing verified findings and next steps without making unverified promises.
                    </p>

                    {customerDraft && (
                      <div className="space-y-2">
                        <textarea
                          rows={6}
                          value={customerDraft}
                          onChange={(e) => setCustomerDraft(e.target.value)}
                          className="w-full rounded-lg border border-slate-200 p-3 text-xs text-slate-800 font-sans leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                        />
                        <div className="flex justify-end">
                          <button
                            onClick={handleCopyCustomerDraft}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                          >
                            {copiedDraft ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                            {copiedDraft ? 'Copied Response' : 'Copy Response Draft'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400">No verification checklist found.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
