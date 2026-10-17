import { BarChart3, Clock, AlertTriangle, CheckCircle2, Users, FolderOpen } from 'lucide-react'

const stats = [
  { label: 'Open Cases', value: '—', icon: FolderOpen, color: 'text-blue-600 bg-blue-50' },
  { label: 'Awaiting Customer', value: '—', icon: Clock, color: 'text-amber-600 bg-amber-50' },
  { label: 'Awaiting Engineering', value: '—', icon: Users, color: 'text-purple-600 bg-purple-50' },
  { label: 'Resolved & Verified', value: '—', icon: CheckCircle2, color: 'text-emerald-600 bg-emerald-50' },
  { label: 'High Priority', value: '—', icon: AlertTriangle, color: 'text-red-600 bg-red-50' },
  { label: 'Avg. Resolution Time', value: '—', icon: BarChart3, color: 'text-slate-600 bg-slate-100' },
]

export function OverviewPage() {
  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Overview</h1>
        <p className="text-sm text-slate-500 mt-1">
          Dashboard metrics and case activity — calculated from live data
        </p>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-5 py-4"
          >
            <div className={`rounded-lg p-2.5 ${stat.color}`}>
              <stat.icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-slate-500">{stat.label}</p>
              <p className="text-xl font-semibold text-slate-900 mt-0.5">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Placeholder panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-4">Case Status Distribution</h2>
          <div className="h-48 flex items-center justify-center text-sm text-slate-400">
            Chart will render from case data
          </div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-4">Recent Activity</h2>
          <div className="h-48 flex items-center justify-center text-sm text-slate-400">
            Timeline will populate from case events
          </div>
        </div>
      </div>
    </div>
  )
}
