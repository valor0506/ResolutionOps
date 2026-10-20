import { useEffect, useState } from 'react'
import {
  Settings as SettingsIcon,
  Cpu,
  Database,
  Shield,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
  Users,
} from 'lucide-react'
import { apiFetch } from '../lib/api'
import { usePersona } from '../contexts/usePersona'
import type { SystemStatus } from '../types/domain'

export function SettingsPage() {
  const { persona, roleDisplay, hasPermission } = usePersona()
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [resetting, setResetting] = useState(false)
  const [resetSuccess, setResetSuccess] = useState<string | null>(null)
  const [resetError, setResetError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false
    apiFetch<SystemStatus>('/settings/status')
      .then((data) => {
        if (!ignore) {
          setStatus(data)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [resetting])

  const handleReset = async () => {
    setResetting(true)
    setResetSuccess(null)
    setResetError(null)
    try {
      const res = await apiFetch<{ success: boolean; message: string }>('/settings/reset-data', {
        method: 'POST',
      })
      setResetSuccess(res.message)
    } catch (err) {
      setResetError((err as Error).message)
    } finally {
      setResetting(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8 max-w-4xl animate-pulse space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded" />
        <div className="h-40 bg-white rounded-xl border border-slate-200" />
        <div className="h-40 bg-white rounded-xl border border-slate-200" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center">
            <SettingsIcon className="h-5 w-5 text-slate-600" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Settings</h1>
            <p className="text-sm text-slate-500 mt-0.5">
              System configuration, AI provider status, and data management
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Active Persona Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-4 w-4 text-blue-600" />
            <h2 className="text-sm font-semibold text-slate-900">Active Persona</h2>
          </div>
          {persona ? (
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-sm font-bold text-white">
                {persona.avatar_initials}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">{persona.display_name}</p>
                <p className="text-xs text-slate-500">{persona.email}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                    {roleDisplay}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Use the sidebar switcher to change roles
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400">No persona loaded</p>
          )}
        </div>

        {/* AI Provider Status Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-4 w-4 text-purple-600" />
            <h2 className="text-sm font-semibold text-slate-900">AI Provider Status</h2>
          </div>
          {status && (
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
                <span className="text-slate-500 flex items-center gap-2">
                  <Cpu className="h-3.5 w-3.5" />
                  Provider
                </span>
                <span className="font-medium text-slate-800">{status.ai.provider}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
                <span className="text-slate-500">Model</span>
                <span className="font-mono font-medium text-slate-800">{status.ai.model}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
                <span className="text-slate-500">Status</span>
                <span className="flex items-center gap-1.5">
                  {status.ai.gemini_available ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                      <span className="font-medium text-emerald-700">Connected</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                      <span className="font-medium text-amber-700">Deterministic Fallback</span>
                    </>
                  )}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 text-xs">
                <span className="text-slate-500">Mode</span>
                <span className={`font-semibold px-2 py-0.5 rounded-full text-[10px] ${
                  status.ai.mode === 'live'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>
                  {status.ai.mode === 'live' ? 'LIVE GEMINI' : 'DETERMINISTIC FALLBACK'}
                </span>
              </div>
              {!status.ai.gemini_available && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
                  <strong>Note:</strong> Set the <code className="bg-amber-100 px-1 rounded">GEMINI_API_KEY</code> environment variable
                  to enable live Gemini AI responses. Without it, the system uses built-in deterministic
                  heuristics that produce the same high-quality grounded outputs.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Data Management Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 mb-4">
            <Database className="h-4 w-4 text-emerald-600" />
            <h2 className="text-sm font-semibold text-slate-900">Data Management</h2>
          </div>
          {status && (
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-slate-900">{status.data.total_customers}</p>
                  <p className="text-[10px] text-slate-500 font-medium uppercase">Customers</p>
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-slate-900">{status.data.total_cases}</p>
                  <p className="text-[10px] text-slate-500 font-medium uppercase">Cases</p>
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-slate-900">{status.data.total_knowledge_articles}</p>
                  <p className="text-[10px] text-slate-500 font-medium uppercase">KB Articles</p>
                </div>
              </div>

              {status.data.is_demonstration_data && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-800 flex items-center gap-2">
                  <Shield className="h-3.5 w-3.5 shrink-0" />
                  All data is synthetic demonstration content generated for testing purposes.
                </div>
              )}

              <div className="pt-3 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-slate-900">Reset Synthetic Data</p>
                    <p className="text-[11px] text-slate-500">
                      Restore all customers, cases, evidence, and hypotheses to their original seeded state.
                    </p>
                  </div>
                  <button
                    onClick={handleReset}
                    disabled={resetting || !hasPermission('system:reset')}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-rose-50 border border-rose-200 px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    <RefreshCw className={`h-3.5 w-3.5 ${resetting ? 'animate-spin' : ''}`} />
                    {resetting ? 'Resetting...' : 'Reset Data'}
                  </button>
                </div>

                {!hasPermission('system:reset') && (
                  <p className="text-[10px] text-amber-600 mt-2">
                    ⚠ Only Platform Engineers can reset data. Switch your persona using the sidebar.
                  </p>
                )}

                {resetSuccess && (
                  <div className="mt-3 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs text-emerald-800 flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
                    {resetSuccess}
                  </div>
                )}

                {resetError && (
                  <div className="mt-3 bg-rose-50 border border-rose-200 rounded-lg p-3 text-xs text-rose-800 flex items-center gap-2">
                    <XCircle className="h-3.5 w-3.5 shrink-0" />
                    {resetError}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Architecture Info Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="h-4 w-4 text-indigo-600" />
            <h2 className="text-sm font-semibold text-slate-900">System Architecture</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="space-y-2">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Frontend</span>
                <span className="font-medium text-slate-800">React 19 + TypeScript + Tailwind v4</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Backend</span>
                <span className="font-medium text-slate-800">Python 3.15 + FastAPI</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Build Tool</span>
                <span className="font-medium text-slate-800">Vite 8</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">AI Provider</span>
                <span className="font-medium text-slate-800">Google Gen AI SDK</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Data Store</span>
                <span className="font-medium text-slate-800">In-Memory (Thread-Safe)</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">API Version</span>
                <span className="font-medium text-slate-800">v0.2.0</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
