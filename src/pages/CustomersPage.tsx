import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, ExternalLink, AlertCircle } from 'lucide-react'
import { apiFetch } from '../lib/api'
import type { Customer } from '../types/domain'

export function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    apiFetch<Customer[]>('/customers')
      .then((data) => {
        setCustomers(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.domain.toLowerCase().includes(search.toLowerCase()) ||
      c.tier.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-8 max-w-7xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Customer Accounts</h1>
          <p className="text-sm text-slate-500 mt-1">
            Environments, SLA commitments, active blockers, and case history.
          </p>
        </div>
        <div className="text-xs text-slate-500 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-xs">
          <strong>5 Active Enterprise & Growth Tenants</strong>
        </div>
      </div>

      <div className="relative max-w-md mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by customer name, domain, or tier..."
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />
      </div>

      {/* Customers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          [...Array(5)].map((_, i) => (
            <div key={i} className="h-64 rounded-xl border border-slate-200 bg-white animate-pulse" />
          ))
        ) : filtered.length === 0 ? (
          <div className="col-span-full rounded-xl border border-slate-200 bg-white p-12 text-center text-slate-400">
            No customers found.
          </div>
        ) : (
          filtered.map((c) => (
            <div
              key={c.id}
              className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-colors"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">{c.name}</h3>
                    <p className="text-xs text-slate-400 font-mono">{c.domain}</p>
                  </div>
                  <span
                    className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${
                      c.tier === 'Enterprise'
                        ? 'bg-purple-50 text-purple-700 border-purple-200'
                        : c.tier === 'Growth'
                        ? 'bg-blue-50 text-blue-700 border-blue-200'
                        : 'bg-slate-50 text-slate-600 border-slate-200'
                    }`}
                  >
                    {c.tier}
                  </span>
                </div>

                <div className="space-y-2 text-xs py-2 border-t border-b border-slate-100 my-3">
                  <div className="flex justify-between">
                    <span className="text-slate-500">SLA Tier</span>
                    <span className="font-medium text-slate-700">{c.sla_tier}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Environment</span>
                    <span className="font-mono text-slate-700 text-[11px] truncate max-w-[180px]">
                      {c.environment}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Version</span>
                    <span className="font-mono text-slate-700">v{c.app_version}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Primary Contact</span>
                    <span className="text-slate-700">{c.primary_contact_name}</span>
                  </div>
                </div>

                {c.active_blockers.length > 0 && (
                  <div className="mb-3 bg-rose-50 border border-rose-200 p-2 rounded text-[11px] text-rose-800">
                    <div className="flex items-center gap-1 font-semibold mb-0.5">
                      <AlertCircle className="h-3 w-3 text-rose-600" />
                      Active Blocker
                    </div>
                    <p className="truncate">{c.active_blockers[0]}</p>
                  </div>
                )}
              </div>

              <div className="pt-2 flex items-center justify-between">
                <Link
                  to={`/cases?customer_id=${c.id}`}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700"
                >
                  <span>View Cases</span>
                  <ExternalLink className="h-3 w-3" />
                </Link>
                <span className="text-[10px] text-slate-400">ID: {c.id}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
