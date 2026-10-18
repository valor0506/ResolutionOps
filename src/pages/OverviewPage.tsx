import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart3,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Users,
  FolderOpen,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react'
import { apiFetch } from '../lib/api'

interface OverviewMetrics {
  total_open_cases: number
  total_cases: number
  cases_awaiting_customer: number
  cases_awaiting_engineering: number
  cases_resolved_and_verified: number
  high_priority_incidents: number
  unowned_cases: number
  average_time_to_resolution_hours: number
  status_distribution: Record<string, number>
  priority_distribution: Record<string, number>
  recent_activity: Array<{
    case_id: string
    title: string
    customer_name: string
    status: string
    priority: string
    updated_at: string
  }>
  is_demonstration_data: boolean
}

export function OverviewPage() {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiFetch<OverviewMetrics>('/overview/metrics')
      .then((data) => {
        setMetrics(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="p-8 max-w-7xl animate-pulse">
        <div className="h-8 w-48 bg-slate-200 rounded mb-4" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-24 bg-white rounded-xl border border-slate-200" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !metrics) {
    return (
      <div className="p-8 max-w-7xl">
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-800">
          <p className="font-medium">Failed to load overview metrics</p>
          <p className="text-sm mt-1">{error ?? 'Unknown error'}</p>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      label: 'Open Cases',
      value: metrics.total_open_cases,
      sub: `${metrics.total_cases} total cases tracked`,
      icon: FolderOpen,
      color: 'text-blue-600 bg-blue-50',
    },
    {
      label: 'Awaiting Customer',
      value: metrics.cases_awaiting_customer,
      sub: 'Missing reproduction or config',
      icon: Clock,
      color: 'text-amber-600 bg-amber-50',
    },
    {
      label: 'Awaiting Engineering',
      value: metrics.cases_awaiting_engineering,
      sub: 'Handoff prepared / in review',
      icon: Users,
      color: 'text-purple-600 bg-purple-50',
    },
    {
      label: 'Resolved & Verified',
      value: metrics.cases_resolved_and_verified,
      sub: 'Passed verification gate',
      icon: CheckCircle2,
      color: 'text-emerald-600 bg-emerald-50',
    },
    {
      label: 'High Priority (Sev 1-2)',
      value: metrics.high_priority_incidents,
      sub: 'Active SLA timers',
      icon: AlertTriangle,
      color: 'text-rose-600 bg-rose-50',
    },
    {
      label: 'Avg. Resolution Time',
      value: `${metrics.average_time_to_resolution_hours}h`,
      sub: 'Target SLA < 4.0h',
      icon: BarChart3,
      color: 'text-slate-600 bg-slate-100',
    },
  ]

  return (
    <div className="p-8 max-w-7xl">
      {/* Header with demo indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Overview Dashboard</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
              Live Synthetic Environment
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Real-time case health, queue latency, and resolution progress.
          </p>
        </div>

        <Link
          to="/cases/CASE-2026-0891"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-medium hover:bg-slate-800 transition-colors shadow-sm"
        >
          <ShieldAlert className="h-4 w-4 text-amber-400" />
          <span>Active Incident: Northstar (CASE-2026-0891)</span>
          <ArrowRight className="h-3.5 w-3.5 ml-1" />
        </Link>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {statCards.map((stat) => (
          <div
            key={stat.label}
            className="flex items-start justify-between rounded-xl border border-slate-200/80 bg-white p-5 shadow-xs"
          >
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{stat.label}</p>
              <p className="text-2xl font-semibold text-slate-900 mt-1">{stat.value}</p>
              <p className="text-xs text-slate-400 mt-1">{stat.sub}</p>
            </div>
            <div className={`rounded-lg p-2.5 ${stat.color}`}>
              <stat.icon className="h-5 w-5" />
            </div>
          </div>
        ))}
      </div>

      {/* Two Column Layout: Status Distribution & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Case Status Breakdown */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-900">Case Status Distribution</h2>
            <span className="text-xs text-slate-400">{metrics.total_cases} total</span>
          </div>

          <div className="space-y-3">
            {Object.entries(metrics.status_distribution).map(([status, count]) => {
              const pct = Math.round((count / metrics.total_cases) * 100)
              return (
                <div key={status}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-medium text-slate-700">{status}</span>
                    <span className="text-slate-500">{count} ({pct}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full ${
                        status === 'Resolved' || status === 'Closed'
                          ? 'bg-emerald-500'
                          : status === 'Investigating'
                          ? 'bg-blue-500'
                          : status === 'Awaiting Engineering'
                          ? 'bg-purple-500'
                          : status === 'Awaiting Customer'
                          ? 'bg-amber-500'
                          : 'bg-slate-400'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Recent Activity Timeline */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-900">Recently Updated Cases</h2>
            <Link to="/cases" className="text-xs font-medium text-blue-600 hover:text-blue-700">
              View all
            </Link>
          </div>

          <div className="divide-y divide-slate-100">
            {metrics.recent_activity.map((item) => (
              <Link
                key={item.case_id}
                to={`/cases/${item.case_id}`}
                className="py-3 flex items-center justify-between group hover:bg-slate-50/60 -mx-2 px-2 rounded-lg transition-colors"
              >
                <div className="min-w-0 pr-4">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold text-slate-800">{item.case_id}</span>
                    <span
                      className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
                        item.priority === 'Critical'
                          ? 'bg-rose-100 text-rose-700'
                          : item.priority === 'High'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {item.priority}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 truncate mt-0.5 font-medium group-hover:text-blue-600 transition-colors">
                    {item.title}
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">{item.customer_name}</p>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-xs font-medium text-slate-700 block">{item.status}</span>
                  <span className="text-[10px] text-slate-400">
                    {new Date(item.updated_at).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
