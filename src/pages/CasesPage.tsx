import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, ShieldAlert, Sparkles, ChevronRight, X, HelpCircle } from 'lucide-react'
import { apiFetch } from '../lib/api'
import type { Case, CasePriority, CaseStatus, IntakeParseResponse } from '../types/domain'

export function CasesPage() {
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [showNewModal, setShowNewModal] = useState(false)

  // Quick intake state
  const [intakeText, setIntakeText] = useState('')
  const [selectedCustomerId, setSelectedCustomerId] = useState('cust-northstar')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<IntakeParseResponse | null>(null)
  const [creating, setCreating] = useState(false)

  const fetchCases = useCallback(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (statusFilter) params.set('status', statusFilter)
    if (priorityFilter) params.set('priority', priorityFilter)

    apiFetch<{ items: Case[]; total: number }>(`/cases?${params.toString()}`)
      .then((data) => {
        setCases(data.items)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [search, statusFilter, priorityFilter])

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCases()
    }, 200)
    return () => clearTimeout(timer)
  }, [fetchCases])

  const handleAnalyzeIntake = async () => {
    if (!intakeText.trim()) return
    setAnalyzing(true)
    try {
      const parsed = await apiFetch<IntakeParseResponse>('/ai/intake-parse', {
        method: 'POST',
        body: JSON.stringify({
          unstructured_complaint: intakeText,
          customer_id: selectedCustomerId,
        }),
      })
      setAnalysisResult(parsed)
      if (parsed.suggested_customer_id) {
        setSelectedCustomerId(parsed.suggested_customer_id)
      }
    } catch (err) {
      alert(`AI Intake Analysis failed: ${(err as Error).message}`)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleCreateCaseFromIntake = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!intakeText.trim()) return

    setCreating(true)
    try {
      const payload = analysisResult
        ? {
            title: analysisResult.concise_summary,
            customer_id: selectedCustomerId,
            priority:
              analysisResult.suggested_severity === 'Sev-1'
                ? 'Critical'
                : analysisResult.suggested_severity === 'Sev-2'
                ? 'High'
                : 'Medium',
            severity: analysisResult.suggested_severity,
            summary: analysisResult.concise_summary,
            expected_behavior: analysisResult.expected_behavior || 'Normal operation',
            actual_behavior: analysisResult.actual_behavior || intakeText,
            symptoms: [analysisResult.concise_summary],
            reproduction_steps: analysisResult.known_reproduction_steps,
            environment: analysisResult.environment || 'production',
            timestamps: analysisResult.available_timestamps,
            request_ids: analysisResult.request_ids,
            missing_information: analysisResult.missing_information,
          }
        : {
            title: intakeText.slice(0, 80),
            customer_id: selectedCustomerId,
            priority: 'High',
            severity: 'Sev-2',
            summary: intakeText,
            expected_behavior: 'Workflow completes without error',
            actual_behavior: intakeText,
            symptoms: [intakeText.slice(0, 60)],
            reproduction_steps: ['Customer submitted complaint via portal'],
            environment: 'production',
            missing_information: ['Exact timestamps', 'Request correlation IDs'],
          }

      await apiFetch<Case>('/cases', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      setShowNewModal(false)
      setIntakeText('')
      setAnalysisResult(null)
      fetchCases()
    } catch (err) {
      alert(`Error creating case: ${(err as Error).message}`)
    } finally {
      setCreating(false)
    }
  }

  const getPriorityBadge = (p: CasePriority) => {
    switch (p) {
      case 'Critical':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'High':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      case 'Medium':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'Low':
        return 'bg-slate-50 text-slate-600 border-slate-200'
    }
  }

  const getStatusBadge = (s: CaseStatus) => {
    switch (s) {
      case 'Investigating':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'Awaiting Customer':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      case 'Awaiting Engineering':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'Fix In Progress':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200'
      case 'Pending Verification':
        return 'bg-cyan-50 text-cyan-700 border-cyan-200'
      case 'Resolved':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200'
      case 'Closed':
        return 'bg-slate-100 text-slate-600 border-slate-200'
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200'
    }
  }

  return (
    <div className="p-8 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Case Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            Search, triage, and investigate customer issues with full evidence grounding.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/cases/CASE-2026-0891"
            className="inline-flex items-center gap-2 rounded-lg border border-amber-300 bg-amber-50/80 px-3.5 py-2 text-xs font-semibold text-amber-900 hover:bg-amber-100/80 transition-colors"
          >
            <ShieldAlert className="h-4 w-4 text-amber-600" />
            Northstar Incident (CASE-2026-0891)
          </Link>
          <button
            onClick={() => {
              setShowNewModal(true)
              setAnalysisResult(null)
            }}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors shadow-xs"
          >
            <Plus className="h-4 w-4" />
            Intake Issue
          </button>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="relative flex-1 min-w-[280px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Case ID, title, customer, or symptom..."
            className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white py-2 px-3 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Investigating">Investigating</option>
            <option value="Awaiting Customer">Awaiting Customer</option>
            <option value="Awaiting Engineering">Awaiting Engineering</option>
            <option value="Fix In Progress">Fix In Progress</option>
            <option value="Pending Verification">Pending Verification</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white py-2 px-3 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          {(search || statusFilter || priorityFilter) && (
            <button
              onClick={() => {
                setSearch('')
                setStatusFilter('')
                setPriorityFilter('')
              }}
              className="text-xs text-slate-500 hover:text-slate-800 underline px-1"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Cases Table */}
      <div className="rounded-xl border border-slate-200/80 bg-white shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/50 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Title & Symptoms</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Owner</th>
                <th className="py-3 px-4 text-right">Updated</th>
                <th className="py-3 px-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {loading ? (
                [...Array(6)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={8} className="py-4 px-4 h-12 bg-slate-50/30" />
                  </tr>
                ))
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No cases match your filters.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-slate-50/60 transition-colors group cursor-pointer"
                    onClick={() => (window.location.href = `/cases/${c.id}`)}
                  >
                    <td className="py-3.5 px-4 font-mono font-medium text-slate-900 whitespace-nowrap">
                      {c.id}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-900 whitespace-nowrap">
                      {c.customer_name}
                    </td>
                    <td className="py-3.5 px-4 max-w-md">
                      <p className="font-medium text-slate-900 truncate group-hover:text-blue-600 transition-colors">
                        {c.title}
                      </p>
                      {c.current_blocker && (
                        <p className="text-[11px] text-amber-700 truncate mt-0.5">
                          ⚠️ Blocker: {c.current_blocker}
                        </p>
                      )}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getPriorityBadge(
                          c.priority
                        )}`}
                      >
                        {c.priority}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border ${getStatusBadge(
                          c.status
                        )}`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 whitespace-nowrap">
                      {c.assigned_owner_name ? (
                        <span>{c.assigned_owner_name.split(' ')[0]}</span>
                      ) : (
                        <span className="text-slate-400 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 text-right whitespace-nowrap">
                      {new Date(c.updated_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </td>
                    <td className="py-3.5 px-2 text-right">
                      <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-slate-600 transition-colors" />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Guided Intake Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-2xl w-full p-6 my-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-slate-900">Intelligent Issue Intake</h3>
              </div>
              <button
                onClick={() => setShowNewModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="text-xs text-slate-500 mb-4">
              Paste raw customer complaints from Zendesk, Salesforce, or Slack. Gemini extracts structured fields,
              validates reproduction steps, and flags missing diagnostic evidence.
            </p>

            <form onSubmit={handleCreateCaseFromIntake} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Customer Account
                </label>
                <select
                  value={selectedCustomerId}
                  onChange={(e) => setSelectedCustomerId(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white py-2 px-3 text-xs text-slate-900"
                >
                  <option value="cust-northstar">Northstar Commerce (Enterprise)</option>
                  <option value="cust-apex">Apex Logistics (Growth)</option>
                  <option value="cust-cloudscale">CloudScale Payments (Enterprise)</option>
                  <option value="cust-retailpulse">RetailPulse Analytics (Starter)</option>
                  <option value="cust-omnistack">OmniStack Media (Growth)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Unstructured Customer Issue Description
                </label>
                <textarea
                  rows={4}
                  value={intakeText}
                  onChange={(e) => setIntakeText(e.target.value)}
                  placeholder="e.g. Our API returned success for order ORD-98421 at 04:15 UTC, but our dashboard still shows it as pending. Request ID was req-8849-a1fc. This is blocking our fulfillment."
                  className="w-full rounded-lg border border-slate-200 p-3 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  required
                />
              </div>

              {/* Analyze with AI Button */}
              <div className="flex justify-between items-center pt-1">
                <button
                  type="button"
                  onClick={handleAnalyzeIntake}
                  disabled={analyzing || !intakeText.trim()}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 text-xs font-semibold hover:bg-blue-100 transition-colors disabled:opacity-50"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  {analyzing ? 'Analyzing with Gemini...' : 'Analyze with AI'}
                </button>

                {analysisResult && (
                  <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    Structured Extraction Complete
                  </span>
                )}
              </div>

              {/* AI Structured Preview Card */}
              {analysisResult && (
                <div className="rounded-xl border border-blue-100 bg-slate-50/70 p-4 space-y-3 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800">Extracted Summary</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-100 text-rose-800 border border-rose-200">
                      Suggested Severity: {analysisResult.suggested_severity}
                    </span>
                  </div>
                  <p className="text-slate-700 bg-white p-2 rounded border border-slate-200 font-medium">
                    {analysisResult.concise_summary}
                  </p>
                  <p className="text-[11px] text-slate-500 italic">
                    Rationale: {analysisResult.severity_rationale}
                  </p>

                  {analysisResult.request_ids.length > 0 && (
                    <div>
                      <span className="font-semibold text-slate-700 block mb-1">Detected IDs:</span>
                      <div className="flex flex-wrap gap-1">
                        {analysisResult.request_ids.map((id) => (
                          <span key={id} className="font-mono text-[10px] bg-slate-200 px-1.5 py-0.5 rounded">
                            {id}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisResult.clarification_questions.length > 0 && (
                    <div className="bg-amber-50 border border-amber-200 p-3 rounded-lg space-y-1">
                      <div className="flex items-center gap-1.5 font-semibold text-amber-900 text-xs">
                        <HelpCircle className="h-3.5 w-3.5" />
                        Targeted Clarification Questions to Ask Customer:
                      </div>
                      <ul className="list-disc list-inside space-y-0.5 text-[11px] text-amber-800">
                        {analysisResult.clarification_questions.map((q, i) => (
                          <li key={i}>{q}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 rounded-lg bg-blue-600 text-xs font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50 shadow-xs"
                >
                  {creating ? 'Creating Case...' : 'Create Validated Case'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
