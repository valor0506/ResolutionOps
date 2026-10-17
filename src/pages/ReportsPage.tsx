import { BarChart3, Clock, CheckCircle2, AlertTriangle, RefreshCw, UserX } from 'lucide-react'

const reportCards = [
  { label: 'Time to First Diagnosis', icon: Clock, description: 'Average time from creation to initial AI-assisted diagnosis' },
  { label: 'Awaiting Customer', icon: AlertTriangle, description: 'Average time cases spend waiting for customer information' },
  { label: 'Awaiting Engineering', icon: RefreshCw, description: 'Average time cases spend waiting for engineering action' },
  { label: 'Handoff Completeness', icon: BarChart3, description: 'Percentage of handoffs with all mandatory fields' },
  { label: 'Verification Success', icon: CheckCircle2, description: 'First-pass verification success rate' },
  { label: 'Unowned Cases', icon: UserX, description: 'Cases without an assigned owner' },
]

export function ReportsPage() {
  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Reports</h1>
        <p className="text-sm text-slate-500 mt-1">
          Resolution metrics and operational insights
        </p>
      </div>

      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 mb-6">
        <p className="text-sm text-amber-800">
          <strong>Seeded data:</strong> Current metrics are calculated from demonstration data.
          Production metrics will be labelled separately.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {reportCards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-slate-200 bg-white p-5"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="rounded-lg bg-slate-100 p-2">
                <card.icon className="h-4 w-4 text-slate-500" />
              </div>
              <h3 className="text-sm font-semibold text-slate-900">{card.label}</h3>
            </div>
            <p className="text-2xl font-semibold text-slate-900 mb-1">—</p>
            <p className="text-xs text-slate-500">{card.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
