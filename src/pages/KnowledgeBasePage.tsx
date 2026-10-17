import { Plus, Search, BookOpen } from 'lucide-react'

export function KnowledgeBasePage() {
  return (
    <div className="p-8 max-w-7xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Knowledge Base</h1>
          <p className="text-sm text-slate-500 mt-1">
            Internal documentation, known issues, and diagnostic guides
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4" />
          New Article
        </button>
      </div>

      <div className="relative max-w-md mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search articles by title, symptoms, or tags..."
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
        <BookOpen className="h-10 w-10 text-slate-300 mx-auto mb-3" />
        <p className="text-sm text-slate-500">Knowledge base articles will appear here</p>
        <p className="text-xs text-slate-400 mt-1">Searchable by title, symptoms, product area, and tags</p>
      </div>
    </div>
  )
}
