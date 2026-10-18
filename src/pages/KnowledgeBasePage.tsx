import { useEffect, useState } from 'react'
import { Search, Tag, ChevronDown, ChevronUp } from 'lucide-react'
import { apiFetch } from '../lib/api'
import type { KnowledgeArticle } from '../types/domain'

export function KnowledgeBasePage() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>('KB-002') // Default expand the Webhook 503 runbook

  useEffect(() => {
    const params = search ? `?query=${encodeURIComponent(search)}` : ''
    apiFetch<KnowledgeArticle[]>(`/knowledge-base${params}`)
      .then((data) => {
        setArticles(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [search])

  return (
    <div className="p-8 max-w-7xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Knowledge Base & Runbooks</h1>
          <p className="text-sm text-slate-500 mt-1">
            Standard operating procedures, diagnostic workflows, and known incident mitigations.
          </p>
        </div>
      </div>

      <div className="relative max-w-md mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by symptom, cause, product area, or tag..."
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />
      </div>

      <div className="space-y-4">
        {loading ? (
          [...Array(4)].map((_, i) => (
            <div key={i} className="h-32 rounded-xl border border-slate-200 bg-white animate-pulse" />
          ))
        ) : articles.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-slate-400">
            No articles match your query.
          </div>
        ) : (
          articles.map((art) => {
            const isExpanded = expandedId === art.id
            return (
              <div
                key={art.id}
                className="rounded-xl border border-slate-200/80 bg-white shadow-xs overflow-hidden transition-all"
              >
                <div
                  onClick={() => setExpandedId(isExpanded ? null : art.id)}
                  className="p-5 flex items-start justify-between gap-4 cursor-pointer hover:bg-slate-50/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                      <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
                        {art.id}
                      </span>
                      <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                        {art.product_area}
                      </span>
                      <span className="text-[11px] text-slate-400">
                        Updated {new Date(art.updated_at).toLocaleDateString()}
                      </span>
                    </div>

                    <h3 className="text-sm font-semibold text-slate-900">{art.title}</h3>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed">{art.description}</p>

                    <div className="flex flex-wrap gap-1.5 mt-2.5">
                      {art.tags.map((t) => (
                        <span
                          key={t}
                          className="inline-flex items-center gap-1 text-[10px] font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200"
                        >
                          <Tag className="h-2.5 w-2.5" />
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  <button className="text-slate-400 hover:text-slate-600 pt-1">
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>
                </div>

                {isExpanded && (
                  <div className="border-t border-slate-100 bg-slate-50/40 p-5 space-y-4 text-xs">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Symptoms */}
                      <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                        <span className="font-semibold text-slate-900 block mb-1.5">Reported Symptoms</span>
                        <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                          {art.symptoms.map((s, idx) => (
                            <li key={idx}>{s}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Known Causes */}
                      <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                        <span className="font-semibold text-slate-900 block mb-1.5">Known Root Causes</span>
                        <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                          {art.known_causes.map((c, idx) => (
                            <li key={idx}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Diagnostic Steps */}
                    <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                      <span className="font-semibold text-slate-900 block mb-1.5">Diagnostic Steps</span>
                      <ol className="list-decimal list-inside space-y-1 text-slate-600 text-[11px]">
                        {art.diagnostic_steps.map((step, idx) => (
                          <li key={idx} className="leading-relaxed">{step}</li>
                        ))}
                      </ol>
                    </div>

                    {/* Resolution Steps */}
                    <div className="bg-emerald-50/50 p-3.5 rounded-lg border border-emerald-200/60">
                      <span className="font-semibold text-emerald-900 block mb-1.5">Standard Resolution Steps</span>
                      <ol className="list-decimal list-inside space-y-1 text-slate-700 text-[11px]">
                        {art.resolution_steps.map((res, idx) => (
                          <li key={idx} className="leading-relaxed">{res}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
